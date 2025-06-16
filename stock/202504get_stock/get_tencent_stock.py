import akshare as ak
import pandas as pd

# 获取阿里巴巴(09988.HK)股票数据
stock_code = "09988"
df = ak.stock_hk_hist(symbol=stock_code, period="daily", start_date="20250101", end_date="20250506", adjust="")

# 保存数据到CSV
csv_file = f"{stock_code}_data.csv"
df.to_csv(csv_file, encoding='utf-8-sig')
print(f"阿里巴巴股票数据已保存到: {csv_file}")

# 显示数据摘要
print("\n数据摘要:")
print(df[['开盘', '收盘', '最高', '最低', '成交量']].describe())
#
#choco install python -yp
