import pandas as pd
import re

# 文件路径
input_file = '20250612/历史成交505-612.csv'
output_file = '股票交易分析模板.csv'

# 读取原始成交数据
raw = pd.read_csv(input_file, dtype=str)

# 只保留证券买入和证券卖出
raw = raw[(raw['买卖标志'] == '证券买入') | (raw['买卖标志'] == '证券卖出')]

# 结果列表
results = []

# 费用提取函数
def extract_fee(text, key):
    if pd.isna(text):
        return 0.0
    # 交易费、印花税等格式如: 交易费:1.29;印花税:0.61
    match = re.search(rf'{key}[：:](\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return 0.0

def extract_multiple_fees(text, keys):
    total = 0.0
    for key in keys:
        total += extract_fee(text, key)
    return total

for _, row in raw.iterrows():
    code = row['证券代码']
    name = row['证券名称']
    date = row['成交日期']
    trade_type = row['买卖标志']
    price = row['成交价格']
    qty = row['成交数量']
    amount = row['成交金额']
    remark = row['备注'] if '备注' in row else ''
    clear_amt = row['清算金额'] if '清算金额' in row else ''

    # 提取手续费和印花税
    fee = extract_multiple_fees(remark, ['交易费', '交易征费', '会财局征费', '换汇尾差'])
    stamp = extract_fee(remark, '印花税')
    # 有些买入/卖出没有备注费用，默认0
    fee = float(fee)
    stamp = float(stamp)
    total_fee = fee + stamp

    # 计算净收益
    try:
        clear_amt_f = float(clear_amt)
        amount_f = float(amount)
    except:
        clear_amt_f = 0.0
        amount_f = 0.0
    if trade_type == '证券卖出':
        net = clear_amt_f - amount_f
    else:
        net = -total_fee

    results.append([
        code, name, date, trade_type, price, qty, amount,
        f'{fee:.2f}', f'{stamp:.2f}', f'{total_fee:.2f}', f'{net:.2f}'
    ])

# 写入模板
header = ['股票代码','股票名称','交易日期','交易类型','交易价格','交易数量','交易金额','手续费','印花税','交易费用合计','净收益']
df_out = pd.DataFrame(results, columns=header)
df_out.to_csv(output_file, index=False, encoding='utf-8-sig')

print('已完成数据提取与转换，结果已写入', output_file) 