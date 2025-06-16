import pandas as pd
import numpy as np
from ta.trend import MACD, SMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
import baostock as bs
import yfinance as yf
from datetime import datetime, timedelta

def validate_date(date_str):
    """
    验证日期格式是否正确
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        return None

def get_stock_data(stock_code, start_date=None, end_date=None, market="A"):
    """
    获取股票数据
    stock_code: 股票代码（如：000001、sh000001、00700.hk）
    start_date: 开始日期，格式：YYYYMMDD
    end_date: 结束日期，格式：YYYYMMDD
    market: 市场，可选 "A"(A股) 或 "HK"(港股)
    """
    try:
        # 验证日期
        start_dt = validate_date(start_date)
        end_dt = validate_date(end_date)
        
        # 如果没有指定日期或日期无效，默认获取最近一年的数据
        if not start_dt:
            start_dt = datetime.now() - timedelta(days=365)
        if not end_dt:
            end_dt = datetime.now()
            
        # 确保开始日期不晚于结束日期
        if start_dt > end_dt:
            start_dt, end_dt = end_dt, start_dt
            
        # 确保结束日期不超过今天
        today = datetime.now()
        if end_dt > today:
            end_dt = today
            
        # 识别市场和股票代码
        # 如果指定了港股市场或代码以.hk结尾
        if market.upper() == "HK" or (isinstance(stock_code, str) and stock_code.lower().endswith('.hk')):
            is_hk = True
            # 提取港股代码
            if stock_code.lower().endswith('.hk'):
                hk_code = stock_code.lower().replace('.hk', '')
            else:
                hk_code = stock_code
                
            # 补足5位数，前面加0
            if len(hk_code) < 5:
                hk_code = hk_code.zfill(5)
                
            # Yahoo Finance的港股代码格式
            yahoo_code = f"{hk_code}.HK"
            print(f"正在获取港股 {yahoo_code} 的数据...")
            
            # 打印日期范围
            print(f"开始日期: {start_dt.strftime('%Y-%m-%d')}, 结束日期: {end_dt.strftime('%Y-%m-%d')}")
            
            # 使用yfinance获取港股数据
            stock = yf.Ticker(yahoo_code)
            df = stock.history(start=start_dt, end=end_dt + timedelta(days=1), interval="1d")
            
            # 打印获取的数据的前几行
            print(df.head())  # 打印获取的数据的前几行
            
            if df.empty:
                print("未找到股票数据，请检查股票代码是否正确")
                return None
                
            # 重命名列名以匹配我们的分析函数
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # 保留需要的列
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            print(f"成功获取了港股 {yahoo_code} 的 {len(df)} 条交易数据")
            return df
            
        else:
            is_hk = False
            # 处理A股代码
            if stock_code.startswith(('sh', 'sz')):
                # 如果已经包含前缀，检查格式 
                if not stock_code.startswith(('sh.', 'sz.')):
                    # 转换为baostock格式
                    prefix = stock_code[:2]
                    code = stock_code[2:]
                    full_code = f"{prefix}.{code}"
                else:
                    full_code = stock_code
            else:
                # 否则根据编号判断添加前缀
                if stock_code.startswith('0'):  # 深市主板
                    full_code = f"sz.{stock_code}"
                elif stock_code.startswith('3'):  # 创业板
                    full_code = f"sz.{stock_code}"
                elif stock_code.startswith('6'):  # 上海主板
                    full_code = f"sh.{stock_code}"
                elif stock_code.startswith('8'):  # 科创板
                    full_code = f"sh.{stock_code}"
                else:
                    print(f"无法识别的股票代码格式：{stock_code}")
                    return None

            print(f"正在获取A股 {full_code} 的数据...")
            
            # 转换日期格式
            bs_start_date = start_dt.strftime('%Y-%m-%d')
            bs_end_date = end_dt.strftime('%Y-%m-%d')
            
            # 登录系统
            bs.login()
            
            try:
                # 获取股票数据
                rs = bs.query_history_k_data_plus(
                    full_code,
                    "date,open,high,low,close,volume",
                    start_date=bs_start_date,
                    end_date=bs_end_date,
                    frequency="d",
                    adjustflag="2"  # 前复权
                )
                
                # 获取数据
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                    
                # 登出系统
                bs.logout()
                
                if len(data_list) == 0:
                    print("未找到股票数据，请检查股票代码是否正确")
                    return None
                    
                # 转换为DataFrame
                df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                
                # 转换数据类型
                for col in ['open', 'high', 'low', 'close']:
                    df[col] = pd.to_numeric(df[col])
                df['volume'] = pd.to_numeric(df['volume'])
                
                # 将日期设置为索引
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                # 确保数据按日期升序排序
                df.sort_index(inplace=True)
                
                print(f"成功获取了A股 {full_code} 的 {len(df)} 条交易数据")
                return df
                
            except Exception as e:
                print(f"获取数据失败：{e}")
                bs.logout()
                return None
    
    except Exception as e:
        print(f"获取股票数据时出错: {e}")
        try:
            bs.logout()
        except:
            pass
        return None

def calculate_technical_indicators(df):
    """
    计算常用技术指标
    df: DataFrame，包含 'close', 'high', 'low', 'volume' 列
    """
    # 1. MACD
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()
    
    # 2. KDJ
    stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
    df['k'] = stoch.stoch()
    df['d'] = stoch.stoch_signal()
    df['j'] = 3 * df['k'] - 2 * df['d']
    
    # 3. RSI
    rsi = RSIIndicator(close=df['close'])
    df['rsi'] = rsi.rsi()
    
    # 4. 布林带
    bb = BollingerBands(close=df['close'])
    df['upper'] = bb.bollinger_hband()
    df['middle'] = bb.bollinger_mavg()
    df['lower'] = bb.bollinger_lband()
    
    # 5. 移动平均线
    df['ma5'] = SMAIndicator(close=df['close'], window=5).sma_indicator()
    df['ma10'] = SMAIndicator(close=df['close'], window=10).sma_indicator()
    df['ma20'] = SMAIndicator(close=df['close'], window=20).sma_indicator()
    df['ma60'] = SMAIndicator(close=df['close'], window=60).sma_indicator()
    
    return df

def generate_signals(df):
    """
    生成交易信号
    """
    signals = pd.DataFrame(index=df.index)
    
    # MACD 金叉死叉
    signals['macd_cross'] = np.where(
        (df['macd'] > df['macd_signal']) & 
        (df['macd'].shift(1) <= df['macd_signal'].shift(1)),
        1,  # 金叉买入信号
        np.where(
            (df['macd'] < df['macd_signal']) & 
            (df['macd'].shift(1) >= df['macd_signal'].shift(1)),
            -1,  # 死叉卖出信号
            0
        )
    )
    
    # RSI 超买超卖
    signals['rsi_signal'] = np.where(
        df['rsi'] < 30, 1,  # 超卖买入信号
        np.where(df['rsi'] > 70, -1, 0)  # 超买卖出信号
    )
    
    # 布林带突破
    signals['bb_signal'] = np.where(
        df['close'] < df['lower'], 1,  # 突破下轨买入信号
        np.where(df['close'] > df['upper'], -1, 0)  # 突破上轨卖出信号
    )
    
    return signals

def print_analysis_results(signals, df):
    """
    打印分析结果
    """
    print("\n=== 技术指标分析结果 ===")
    
    # 获取最新的指标值
    latest = df.iloc[-1]
    print(f"\n最新技术指标值:")
    print(f"MACD: {latest['macd']:.2f} (信号线: {latest['macd_signal']:.2f}, 柱状值: {latest['macd_hist']:.2f})")
    print(f"KDJ: K={latest['k']:.2f}, D={latest['d']:.2f}, J={latest['j']:.2f}")
    print(f"RSI: {latest['rsi']:.2f}")
    print(f"布林带: 上轨={latest['upper']:.2f}, 中轨={latest['middle']:.2f}, 下轨={latest['lower']:.2f}")
    print(f"均线: MA5={latest['ma5']:.2f}, MA10={latest['ma10']:.2f}, MA20={latest['ma20']:.2f}, MA60={latest['ma60']:.2f}")
    
    print("\n=== 最近的交易信号 ===")
    recent_signals = signals[signals != 0].tail(5)
    if not recent_signals.empty:
        print("\n最近5个交易信号:")
        print(recent_signals)
    else:
        print("最近没有产生交易信号")

def main():
    """
    主函数，提供交互式界面
    """
    while True:
        print("\n=== 股票技术分析系统 ===")
        print("请输入股票代码:")
        print("示例股票代码：")
        print("  A股：")
        print("    上证指数：sh000001")
        print("    深证成指：sz399001")
        print("    平安银行：000001")
        print("    贵州茅台：600519")
        print("    宁德时代：300750")
        print("  港股：")
        print("    腾讯控股：00700.hk")
        print("    阿里巴巴：09988.hk")
        print("    美团：03690.hk")
        print("    小米集团：01810.hk")
        print("输入 'q' 退出程序")
        
        stock_code = input("股票代码: ").strip()
        
        if stock_code.lower() == 'q':
            print("程序已退出")
            break
            
        if not stock_code:
            print("股票代码不能为空！")
            continue
            
        # 判断市场
        market = "HK" if stock_code.lower().endswith('.hk') else "A"
            
        # 处理股票代码格式
        if market == "A":
            if stock_code.startswith(('sh', 'sz')):
                if len(stock_code) != 8 and len(stock_code) != 9:  # sh/sz + 6位数字或带点号
                    print("A股代码格式错误！应为 sh/sz + 6位数字，如：sh000001")
                    continue
            elif not (len(stock_code) == 6 and stock_code.isdigit()):
                print("A股代码格式错误！应为6位数字，如：000001")
                continue
        
        # 获取日期范围（可选）
        print("\n请输入起始日期（可选，格式：YYYYMMDD，直接回车使用默认值）")
        print("例如：20230101 表示 2023年1月1日")
        start_date = input("起始日期: ").strip()
        
        if start_date and not validate_date(start_date):
            print("起始日期格式错误！将使用默认值（一年前）")
            start_date = None
            
        print("请输入结束日期（可选，格式：YYYYMMDD，直接回车使用默认值）")
        print("例如：20240321 表示 2024年3月21日")
        end_date = input("结束日期: ").strip()
        
        if end_date and not validate_date(end_date):
            print("结束日期格式错误！将使用默认值（今天）")
            end_date = None
        
        # 获取股票数据
        print("\n正在获取股票数据，请稍候...")
        df = get_stock_data(stock_code, start_date, end_date, market)
        
        if df is not None and not df.empty:
            print(f"\n成功获取 {len(df)} 条交易数据")
            
            print("正在计算技术指标...")
            # 计算技术指标
            df = calculate_technical_indicators(df)
            
            print("正在生成交易信号...")
            # 生成交易信号
            signals = generate_signals(df)
            
            # 打印分析结果
            print_analysis_results(signals, df)
        else:
            print("\n提示：")
            if market == "HK":
                print("1. 请确保输入的是有效的港股股票代码")
                print("2. 港股代码格式为：5位数字 + .hk，如：00700.hk")
            else:
                print("1. 请确保输入的是有效的A股股票代码")
                print("2. A股代码格式为：6位数字，如：000001")
            print("3. 新股可能没有足够的历史数据")
            print("4. 如果确认股票代码无误，可能是网络问题，请稍后重试")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()