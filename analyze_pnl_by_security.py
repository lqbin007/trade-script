import pandas as pd

# 文件路径
trade_file = '202506对账单.csv'
pos_file = '股票持仓模板.csv'
out_file = '202506对账单_盈亏统计.csv'

# 读取交易流水
raw = pd.read_csv(trade_file, dtype=str)
raw = raw[raw['业务名称'].isin(['证券买入', '证券卖出'])]
for col in ['成交金额','成交数量','手续费','印花税','过户费','交易所清算费','附加费']:
    raw[col] = pd.to_numeric(raw[col], errors='coerce').fillna(0)

# 读取持仓表
pos = pd.read_csv(pos_file, dtype=str, encoding='gbk')
for col in ['持仓数量','平均持仓成本','当前价格']:
    pos[col] = pd.to_numeric(pos[col], errors='coerce').fillna(0)

# 分组统计已实现部分
summary = []
for (code, name), group in raw.groupby(['证券代码','证券名称']):
    buy = group[group['业务名称']=='证券买入']
    sell = group[group['业务名称']=='证券卖出']
    buy_amt = buy['成交金额'].sum()
    sell_amt = sell['成交金额'].sum()
    buy_qty = buy['成交数量'].sum()
    sell_qty = sell['成交数量'].sum()
    buy_fee = buy['手续费'].sum()
    sell_fee = sell['手续费'].sum()
    sell_tax = sell['印花税'].sum()
    sell_transfer = sell['过户费'].sum()
    sell_clear = sell['交易所清算费'].sum()
    sell_extra = sell['附加费'].sum()
    total_fee = buy_fee + sell_fee + sell_tax + sell_transfer + sell_clear + sell_extra
    realized_pnl = sell_amt - buy_amt - total_fee
    # 查找当前持仓
    pos_row = pos[(pos['股票代码'].astype(str)==str(code)) & (pos['股票名称']==name)]
    if not pos_row.empty:
        cur_qty = int(round(pos_row.iloc[0]['持仓数量']))
        cur_price = pos_row.iloc[0]['当前价格']
        avg_cost = pos_row.iloc[0]['平均持仓成本']
        # 未实现盈亏 = 当前持仓数量 * (当前价格 - 平均持仓成本)
        unrealized_pnl = cur_qty * (cur_price - avg_cost)
    else:
        cur_qty = 0
        cur_price = 0
        avg_cost = 0
        unrealized_pnl = 0
    total_pnl = realized_pnl + unrealized_pnl
    total_yield = (total_pnl / buy_amt * 100) if buy_amt != 0 else 0
    summary.append([
        code, name,
        int(round(buy_amt)), int(round(sell_amt)), int(round(buy_qty)), int(round(sell_qty)),
        int(round(buy_fee)), int(round(sell_fee)), int(round(sell_tax)), int(round(sell_transfer)),
        int(round(sell_clear)), int(round(sell_extra)), int(round(realized_pnl)), int(round(unrealized_pnl)),
        int(round(total_pnl)), int(round(total_yield)), int(round(cur_qty)), int(round(cur_price)), int(round(avg_cost))
    ])

# 输出
header = ['证券代码','证券名称','买入总额','卖出总额','买入数量','卖出数量','买入手续费','卖出手续费','卖出印花税','卖出过户费','卖出清算费','卖出附加费','已实现盈亏','未实现盈亏','总盈亏','总收益率(%)','当前持仓数量','当前价格','平均持仓成本']
df_out = pd.DataFrame(summary, columns=header)
df_out.to_csv(out_file, index=False, encoding='utf-8-sig')

print('已完成详细盈亏统计（含未实现部分，数字已取整），结果已写入', out_file) 