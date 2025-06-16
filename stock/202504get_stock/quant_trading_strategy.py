import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt
from datetime import datetime

class DualMovingAverageStrategy(bt.Strategy):
    params = (
        ('fast', 5),    # 快速均线周期
        ('slow', 20),   # 慢速均线周期
        ('stop_loss', 0.03),  # 3%止损
        ('take_profit', 0.08), # 8%止盈
        ('volume_filter', 1.5) # 交易量过滤倍数
    )

    def __init__(self):
        # 定义均线指标
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.fast)
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"买入执行 @ {order.executed.price:.2f}")
            elif order.issell():
                self.log(f"卖出执行 @ {order.executed.price:.2f}")
            self.bar_executed = len(self)
        
        self.order = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt}, {txt}")

    def next(self):
        self.log(f"收盘价: {self.data.close[0]:.2f}, 快线: {self.fast_ma[0]:.2f}, 慢线: {self.slow_ma[0]:.2f}, 成交量: {self.data.volume[0]:.2f}")
        
        if self.order:
            return
            
        if not self.position:
            # 在指定价格建仓200股
            print(f"当前价: {self.data.close[0]:.2f}, 建仓条件: <=10570")
            if self.data.close[0] <= 10570:
                print(f"触发建仓条件: 当前价{self.data.close[0]:.2f} <= 10570")
                # 调整交易数量为1股以匹配资金规模
                self.order = self.buy(size=1, price=self.data.close[0], exectype=bt.Order.Limit)
                self.stop_loss = self.data.close[0] * (1 - self.p.stop_loss)
                self.take_profit = self.data.close[0] * (1 + self.p.take_profit)
                print(f"设置止损价: {self.stop_loss:.2f}, 止盈价: {self.take_profit:.2f}")
                print(f"可用资金: {self.broker.getcash():.2f}, 所需资金: {self.data.close[0] * 1:.2f}")
        else:
            if (self.crossover < 0 or 
                self.data.close[0] <= self.stop_loss or 
                self.data.close[0] >= self.take_profit):
                self.order = self.close()

def backtest(data_file):
    # 创建回测引擎
    cerebro = bt.Cerebro()
    
    # 加载数据并转换列名
    df = pd.read_csv(data_file, parse_dates=['日期'], index_col='日期')
    print("原始数据样例:")
    print(df.head())
    
    # 统一价格单位处理
    print("统一价格单位处理: 将价格乘以100")
    df['开盘'] = df['开盘'] * 100
    df['收盘'] = df['收盘'] * 100 
    df['最高'] = df['最高'] * 100
    df['最低'] = df['最低'] * 100
    
    # 重命名列以符合backtrader要求
    df = df.rename(columns={
        '开盘': 'open',
        '收盘': 'close', 
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume'
    })
    # 确保数据按日期排序
    df = df.sort_index()
    # 添加必要的列
    df['openinterest'] = 0
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 使用索引作为日期
        open=0, high=1, low=2, close=3, volume=4, openinterest=5
    )
    cerebro.adddata(data)
    
    # 添加策略
    cerebro.addstrategy(DualMovingAverageStrategy)
    
    # 设置初始资金
    cerebro.broker.setcash(20000.0)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    # 运行回测
    print('初始资金: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('最终资金: %.2f' % cerebro.broker.getvalue())
    
    # 打印分析结果
    strat = results[0]
    print('夏普比率:', strat.analyzers.sharpe.get_analysis()['sharperatio'])
    print('最大回撤:', strat.analyzers.drawdown.get_analysis()['max']['drawdown'])
    print('年化收益率:', strat.analyzers.returns.get_analysis()['rnorm100'])
    
    # 可视化
    cerebro.plot(style='candlestick')

if __name__ == '__main__':
    # 使用之前获取的阿里巴巴数据
    backtest('09988_data.csv')
