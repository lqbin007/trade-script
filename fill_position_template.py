import pandas as pd

# 文件路径
input_file = '613.csv'
output_file = '股票持仓模板.csv'

# 读取原始持仓数据
raw = pd.read_csv(input_file, dtype=str)

# 过滤掉"标准券"等非股票/ETF类资产
raw = raw[~raw['证券名称'].str.contains('标准券', na=False)]

# 只保留持仓数量大于0的行
raw = raw[raw['参考持股'].astype(float) > 0]

# 字段映射
mapping = {
    '股票代码': '证券代码',
    '股票名称': '证券名称',
    '持仓数量': '参考持股',
    '平均持仓成本': '成本价',
    '当前价格': '当前价',
    '持仓市值': '最新市值',
    '持仓成本': '当前成本',
    '未实现收益': '浮动盈亏',
    '未实现收益率': '盈亏比例(%)',
}

# 构建输出DataFrame
out_df = pd.DataFrame()
for out_col, in_col in mapping.items():
    out_df[out_col] = raw[in_col]

# 写入模板，覆盖原文件
out_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print('已完成持仓数据提取与转换，结果已写入', output_file) 