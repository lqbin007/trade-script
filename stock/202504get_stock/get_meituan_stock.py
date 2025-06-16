import akshare as ak
import pandas as pd
from datetime import datetime

def get_user_input():
    """获取用户输入的股票代码和时间范围"""
    print("股票数据下载工具")
    print("="*30)
    
    stock_code = input("请输入港股代码(如:03690): ").strip()
    start_date = input("请输入开始日期(YYYYMMDD,如:20250101): ").strip()
    end_date = input("请输入结束日期(YYYYMMDD,默认为今日): ").strip()
    
    # 设置默认结束日期为今日
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    
    return stock_code, start_date, end_date

def validate_input(stock_code, start_date, end_date):
    """验证用户输入"""
    try:
        # 验证股票代码为数字
        if not stock_code.isdigit():
            raise ValueError("股票代码必须为数字")
            
        # 验证日期非空且格式正确
        if not start_date:
            raise ValueError("开始日期不能为空")
        datetime.strptime(start_date, "%Y%m%d")
        
        if end_date:  # 结束日期可为空(已设置默认值)
            datetime.strptime(end_date, "%Y%m%d")
        
        return True
    except ValueError as e:
        print(f"输入错误: {e}")
        return False

def main():
    # 获取用户输入
    stock_code, start_date, end_date = get_user_input()
    
    # 验证输入
    if not validate_input(stock_code, start_date, end_date):
        return
    
    try:
        # 获取股票数据
        df = ak.stock_hk_hist(
            symbol=stock_code, 
            period="daily", 
            start_date=start_date, 
            end_date=end_date, 
            adjust=""
        )
        
        # 保存数据到CSV
        csv_file = f"{stock_code}_data.csv"
        df.to_csv(csv_file, encoding='utf-8-sig')
        print(f"\n{stock_code}股票数据已保存到: {csv_file}")
        
        # 显示数据摘要
        print("\n数据摘要:")
        print(df[['开盘', '收盘', '最高', '最低', '成交量']].describe())
        
    except Exception as e:
        print(f"获取数据失败: {e}")

if __name__ == "__main__":
    main()
