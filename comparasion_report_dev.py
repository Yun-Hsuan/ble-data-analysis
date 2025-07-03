import pandas as pd
from pathlib import Path
from openpyxl.utils import get_column_letter
from openpyxl.styles import NamedStyle, numbers

def generate_tenant_comparison_report(input_file: str, output_path: str):
    """
    Generate a comparison report for all tenants based on the overview report.
    Group tenants by floor and create separate sheets for each floor.
    
    :param input_file: Path to the overview report Excel file.
    :param output_path: Path to save the comparison report.
    """
    # 读取概述报告
    print(f"Reading overview report: {input_file}")
    excel_data = pd.ExcelFile(input_file, engine='openpyxl')
    
    # 初始化存储所有柜位数据的字典，按楼层分组
    floor_data = {}
    
    # 处理每个工作表（柜位）
    for sheet_name in excel_data.sheet_names:
        print(f"Processing sheet: {sheet_name}")
        df = excel_data.parse(sheet_name)
        
        # 提取柜位名称和楼层
        tenant_name = sheet_name
        floor = df["樓層"].iloc[0] if "樓層" in df.columns else "其他"  # 获取楼层信息
        
        # 提取指标数据
        metrics = {
            "路過數 A": df["路過數 A"].sum() if "路過數 A" in df.columns else 0,
            "靠櫃數 B": df["靠櫃數 B"].sum() if "靠櫃數 B" in df.columns else 0,
            "靠櫃率 B/A": df["靠櫃數 B"].sum()/df["路過數 A"].sum() if "靠櫃率 B/A" in df.columns else 0,
            "停留數 C": df["停留數 C"].sum() if "停留數 C" in df.columns else 0,
            "停留率 C/A": df["停留數 C"].sum()/df["路過數 A"].sum() if "停留率 C/B" in df.columns else 0,
            "停留率 C/B": df["停留數 C"].sum()/df["靠櫃數 B"].sum() if "停留率 C/B" in df.columns else 0,
            "交易數 D": df["交易數 D"].sum() if "交易數 D" in df.columns else 0,
            "提袋率 D/C": df["交易數 D"].sum() / df["停留數 C"].sum() if "提袋率 D/C" in df.columns else 0,
            "提袋率 D/B": df["交易數 D"].sum() / df["靠櫃數 B"].sum() if "提袋率 D/B" in df.columns else 0,
            "平均停留 (秒)": df["平均停留 (秒)"].mean() if "平均停留 (秒)" in df.columns else 0,
        }
        
        # 将数据添加到对应楼层的字典中
        if floor not in floor_data:
            floor_data[floor] = {}
        floor_data[floor][tenant_name] = metrics
    
    # 写入比较表到Excel文件
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # 为每个楼层创建一个工作表
        for floor, tenants_data in floor_data.items():
            # 创建该楼层的比较表
            floor_df = pd.DataFrame(tenants_data)  # 不转置，保持原有格式
            
            # 写入工作表
            sheet_name = f"{floor}樓層比較"
            floor_df.to_excel(writer, sheet_name=sheet_name)
            
            # 获取工作表
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # 设置格式
            for row_idx in range(2, len(floor_df) + 2):  # 排除标题行
                for col_idx in range(2, len(floor_df.columns) + 2):  # 跳过索引列
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    row_name = str(floor_df.index[row_idx-2])
                    if any(rate in row_name for rate in ["率", "Rate"]):
                        cell.number_format = "0.00%"
                    elif row_name == "平均停留 (秒)":
                        cell.number_format = "0.00"
    
    print(f"\nComparison report successfully generated: {output_path}")

if __name__ == "__main__":
    generate_tenant_comparison_report(
        input_file="./daily_reports/tenant_overview_report_0512_0518.xlsx",
        output_path="./daily_reports/tenant_comparison_report_0512_0518.xlsx"
    )
