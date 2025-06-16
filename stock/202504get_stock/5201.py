import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('09988_data.csv', index_col=1, parse_dates=True)
df = df[['开盘','收盘','最高','最低','成交量']]
df.columns = ['Open','Close','High','Low','Volume']

# 计算均线
df['MA5'] = df['Close'].rolling(5).mean()
df['MA10'] = df['Close'].rolling(10).mean()
df['MA20'] = df['Close'].rolling(20).mean()

# 计算MACD
def calc_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = 2 * (dif - dea)
    return dif, dea, macd

df['DIF'], df['DEA'], df['MACD'] = calc_macd(df['Close'])

# 读取背离信号
df_div = pd.read_csv('09988_divergence.csv', index_col=1, parse_dates=True)
df['divergence_signal'] = df_div.reindex(df.index)['divergence_signal']

# 生成买入信号
df['macd_golden_cross'] = (df['DIF'] > df['DEA']) & (df['DIF'].shift(1) <= df['DEA'].shift(1))
df['ma_bull'] = (df['MA5'] > df['MA10']) & (df['MA10'] > df['MA20'])
df['buy_signal'] = (df['divergence_signal'] == 1) & df['macd_golden_cross'] & df['ma_bull']

# 输出买入信号日期和价格
buy_points = df[df['buy_signal']]
print("买入信号：")
print(buy_points[['Open','Close','High','Low']])

# 可选：画图标记买点
import mplfinance as mpf
apds = []
buy_marker = np.full(len(df), np.nan)
for idx in buy_points.index:
    buy_marker[df.index.get_loc(idx)] = df.loc[idx, 'Low']
apds.append(mpf.make_addplot(buy_marker, type='scatter', markersize=120, marker='^', color='green'))

mpf.plot(df, type='candle', volume=True, addplot=apds, style='yahoo', title='组合量化买点', figratio=(16,9), figscale=1.2, mav=(5,10,20), savefig='combo_quant_buy.png')