import pandas as pd
import mplfinance as mpf
import numpy as np
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 指定黑体
matplotlib.rcParams['axes.unicode_minus'] = False    # 正常显示负号

# 读取数据
df = pd.read_csv('09988_data.csv', index_col=1, parse_dates=True)
df_div = pd.read_csv('09988_divergence.csv', index_col=1, parse_dates=True)

# 保证索引为日期
df = df[['开盘','收盘','最高','最低','成交量']]
df.columns = ['Open','Close','High','Low','Volume']

# 只取最近60天
df_recent = df.iloc[-60:]
df_div_recent = df_div.reindex(df_recent.index)

# 设定阈值（如5%）
threshold = 0.05
window = 5

# 只保留背离后5天内最大涨跌幅绝对值超过阈值的背离点
def filter_signals(div_df, price_df, signal, threshold, window):
    filtered_idx = []
    for idx in div_df[div_df['divergence_signal']==signal].index:
        if idx not in price_df.index:
            continue
        pos = price_df.index.get_loc(idx)
        close = price_df.loc[idx, 'Close']
        # 取后window天
        future = price_df.iloc[pos+1:pos+1+window]
        if not future.empty:
            max_up = (future['High'].max() - close) / close
            max_down = (future['Low'].min() - close) / close
            if abs(max_up) >= threshold or abs(max_down) >= threshold:
                filtered_idx.append(idx)
    return filtered_idx

pos_idx = filter_signals(df_div_recent, df_recent, 1, threshold, window)
neg_idx = filter_signals(df_div_recent, df_recent, -1, threshold, window)

# 生成和df_recent等长的标记Series
pos_marker = np.full(len(df_recent), np.nan)
neg_marker = np.full(len(df_recent), np.nan)
for idx in pos_idx:
    pos_marker[df_recent.index.get_loc(idx)] = df_recent.loc[idx, 'High']
for idx in neg_idx:
    neg_marker[df_recent.index.get_loc(idx)] = df_recent.loc[idx, 'Low']

apds = [
    mpf.make_addplot(pos_marker, type='scatter', markersize=80, marker='^', color='red', alpha=0.8),
    mpf.make_addplot(neg_marker, type='scatter', markersize=80, marker='v', color='blue', alpha=0.8)
]

# 画K线+量柱+背离标记
mpf.plot(df_recent, type='candle', volume=True, addplot=apds, style='yahoo', title='09988 近60天量价K线与背离', figratio=(16,9), figscale=1.2, mav=(5,10,20), savefig='09988_kline_divergence_recent.png')