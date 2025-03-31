import pandas as pd
import json

def excel_to_json(input_file, output_file, start_row, end_row):
    # 读取 Excel 文件
    df = pd.read_excel(input_file)
    
    # 确保行号在有效范围内
    start_row = max(start_row, 0)  # 避免负数
    end_row = min(end_row, len(df) - 1)  # 避免超出范围
    
    # 提取指定范围的数据
    data = df.iloc[start_row:end_row + 1]
    
    # 构造 JSON 数据
    json_data = []
    for _, row in data.iterrows():
        json_data.append({
            "instruct": "请你将以下老年人口语转换成书面语。",
            "input": str(row["原口语文本"]),
            "output": str(row["翻译结果"])
        })
    
    # 写入 JSON 文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

# 示例调用
excel_to_json(
    input_file="processed_file.xlsx",
    output_file="train.json",
    start_row=1,  # 假设数据从第 2 行开始（0-based 或 1-based 取决于需求）
    end_row=500    # 提取到第 11 行. 行数=end-start+1 .. ps设置成500好像会多翻译一行
)