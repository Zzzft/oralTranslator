import pandas as pd
import requests
import json
from config import DEEPSEEK_API_KEY

def process_excel():
    # 读取Excel文件
    file_path = 'dataset/data.xlsx'  # 替换为你的文件路径
    df = pd.read_excel(file_path)
    
    # 获取用户输入
    while True:
        try:
            start_row = 189 - 2  # 转换为0-based索引
            num_rows = 50
            
            if start_row < 0 or start_row >= len(df):
                print("错误：起始行号超出范围")
                continue
                
            end_row = min(start_row + num_rows, len(df))
            actual_rows = end_row - start_row
            print(f"即将处理从Excel行号{start_row+2}开始的{actual_rows}条数据")
            break
            
        except ValueError:
            print("请输入有效的数字")

    # API配置
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # 提示词模板
    prompt_template = """请你按如下规则将以下老年人的口语文本翻译成亲切易懂的语言：
    阅读并分析口语所在上下文内容，用中文总结段落主旨。确认你已理解上下文关系和核心观点，针对需要翻译的口语句子，在保持与原文的句意一致的前提下按如下规则进行翻译。
    规则：
    1.删除口语中重复冗余的词汇，删除无意义的插入语。
    例如：
    - 嗯，那个，就是吧，我觉得这个事情呢，挺好的。（"嗯"，"那个"，"就是吧"，"呢" 是没有实质意义的填充词）
    - 所以我刚才接着刚才说，所以他们基本都走。（刚才重复冗余）

    2.请你将非正式性的口语词翻译成中等正式程度的书面表达，保留自然口语基调，将带有地域或代际特征的词语翻译成当代通用汉语。
    对于有多种含义的口语词汇，根据上下文选择最自然且无歧义的翻译。
    例如：
    - 她虚岁99岁走的。（“走的”即“去世”的口语说法）
    - 这是09年的一个光是我们老爷们儿第二代和老娘照的，这是我们连三辈儿四辈儿都有的。（三辈儿、四辈儿即第三代、第四代人，老爷们儿指兄弟们，老娘指母亲）

    3. 请你将指代模糊的人称代词替换为清晰的表达，根据句意推断出人称代词实际指向的人物。如果上下文没有明确的指代对象，就保留原来的人称代词。
    例如：
    - 他告诉他，让他早点回家。（这里的三个“他”指代不明，需要根据上下文确定三个“他”分别指谁）
    - 我弟妹说让我们把家腾干净了，我们要来住了（第二个“我们”是指说话的人，即弟妹他们）
    - 他都所以所以在这种情况下，老三他们家提出来这个房子就应该是我们的。（这里的“我们”是指说话的人，即老三他们家）
    - 从我们兄弟姐妹来说，受母亲的影响比较大，因为父亲那时候走的时候，他们有时候大部分时间在外地，刚回来也都挺忙的，正在中年，所以对父亲的印象不是特别深刻。(“他们”是指受父母影响的人，即“我们兄弟姐妹”)

    4. 口语表达存在表达不准确或口误后自我修正的情况，对于这种前后表达存在冲突的情况，请保留修正后正确的结果。
    例如：
    - 我们哥五个哥六个觉得一定得这么办。（前半句“哥五个”为口误，后半句“哥六个”为修正，翻译后只需保留修正的后半句）

    5. 当口语为了简化表达而省略一些句子成分（如主语、谓语或宾语）时，请你根据句意将这些成分补充完整。
    例如：
    - 母亲一直跟我在一起。（省略了（生活）在一起）
    - 6个4个党员。（省略了6个（兄弟姐妹里））

    6.当句子成分残缺（缺乏主谓宾或定状补）或句子结构复杂（多个从句或插入语）导致句子意思难以理解时，请你提取主干信息，调整语序，适当删减，使得句子亲切易懂。
    例如：
    - 母亲的影响尤其我们日后都退了休了又跟他在一起生活，影响越来越深刻了（成分残缺导致听者难以理解是母亲对谁的影响，应补充上母亲“对我们的”影响）。
    - 南市住的话，她要是回一趟咸水沽的话，每次回去一趟起码得将近半天差不多，所以她也基本上不在家里，因为他们也是三班倒，那阵都是工人嘛。（“因为他们也是三班倒，那阵都是工人嘛”结构混乱，不易理解，实际后半句是对前半句的补充，是说“那时候大家都是工人”）
    三班倒，所以这个时间基本上一个星期两个星期，所谓有个大大公休吧，那阵倒班，回家一次。（句子结构混乱，表述含糊，应该翻译为：她那时候“三班倒”，所以通常一到两个星期遇到大公休才能回家一次）

    你需要翻译的口语：
    {oral_sentence}

    口语所在上下文：
    {context}

    仅输出指定口语的翻译结果文本，不要输出思考过程，不要输出解释。"""

    # 进度计数器
    processed = 0
    
    # 遍历指定范围的行
    for idx in range(start_row, end_row):
        row = df.iloc[idx]
        try:
            # 动态生成提示词
            current_prompt = prompt_template.format(
                oral_sentence=row["原口语文本"],
                context=row["口语文本所在上下文"]
            )
            
            # 构造请求
            payload = {
                "model": "deepseek-ai/DeepSeek-R1",
                "messages": [{"role": "user", "content": current_prompt}],
                "temperature": 0.2
            }
            
            # 发送请求
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # 解析结果
            data = json.loads(response.text)
            translation = data["choices"][0]["message"]["content"]
            
            # 写入结果列
            df.at[idx, "翻译结果"] = translation
            processed += 1
            
            # 打印进度
            print(f"已处理 {processed}/{actual_rows} 条，当前Excel行号：{idx+2}")
            
        except requests.exceptions.HTTPError as e:
            print(f"API请求失败（行号{idx+2}）：{str(e)}")
            df.at[idx, "翻译结果"] = "API请求失败"
        except KeyError:
            print(f"响应解析失败（行号{idx+2}）")
            df.at[idx, "翻译结果"] = "解析失败"
        except Exception as e:
            print(f"未知错误（行号{idx+2}）：{str(e)}")
            df.at[idx, "翻译结果"] = "处理失败"

    # 保存结果（新文件名带时间戳）
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    output_file = f"processed_file_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n处理完成！结果已保存到 {output_file}")

if __name__ == "__main__":
    process_excel()