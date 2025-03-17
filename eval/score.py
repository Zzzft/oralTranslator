import pandas as pd
import torch
from bert_score import BERTScorer
from tqdm import tqdm

def calculate_bertscore():
    # 读取Excel文件
    df = pd.read_excel('processed_file_202503161958.xlsx')  # 替换为你的文件路径
    
    # 获取用户输入
    while True:
        try:
            start_row = 49
            num_rows = 100
            
            # 转换为0-based索引
            start_idx = start_row - 2
            if start_idx < 0 or start_idx >= len(df):
                print(f"错误：起始行号超出有效范围（2-{len(df)+1}）")
                continue
                
            end_idx = min(start_idx + num_rows, len(df))
            actual_rows = end_idx - start_idx
            print(f"即将处理从Excel行号{start_row}开始的{actual_rows}条数据")
            break
            
        except ValueError:
            print("请输入有效的数字")

    # 初始化BERTScorer
    scorer = BERTScorer(
        model_type='bert-base-chinese',
        lang='zh',
        device='cuda' if torch.cuda.is_available() else 'cpu',
        rescale_with_baseline=True
    )
    
    # 提取指定范围的文本
    references = df['翻译后的书面语文本'].iloc[start_idx:end_idx].tolist()
    candidates = df['翻译结果'].iloc[start_idx:end_idx].tolist()
    
    # 批量计算BERTScore
    batch_size = 64
    scores = {'P': [], 'R': [], 'F1': []}
    
    progress_bar = tqdm(total=len(candidates), 
                      desc=f"处理行 {start_row}-{start_row+actual_rows-1}",
                      unit="row")
    
    for i in range(0, len(candidates), batch_size):
        batch_refs = references[i:i+batch_size]
        batch_cands = candidates[i:i+batch_size]
        
        P, R, F1 = scorer.score(batch_cands, batch_refs)
        
        scores['P'].extend(P.tolist())
        scores['R'].extend(R.tolist())
        scores['F1'].extend(F1.tolist())
        
        progress_bar.update(len(batch_cands))
    
    progress_bar.close()
    
    # 将结果写回指定行范围
    df.loc[start_idx:end_idx-1, 'BERTScore_P'] = [round(p, 4) for p in scores['P']]
    df.loc[start_idx:end_idx-1, 'BERTScore_R'] = [round(r, 4) for r in scores['R']]
    df.loc[start_idx:end_idx-1, 'BERTScore_F1'] = [round(f1, 4) for f1 in scores['F1']]
    
    # 保存结果（新文件名带范围标记）
    output_file = f"scored_results_{start_row}_to_{start_row+actual_rows-1}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n处理完成！结果已保存到 {output_file}")

if __name__ == '__main__':
    calculate_bertscore()