import pandas as pd

def detect_volume_price_divergence(data, lookback=14):
    """检测量价背离"""
    data['price_change'] = data['收盘'].pct_change()
    data['volume_change'] = data['成交量'].pct_change()
    data['divergence_signal'] = 0  # 0:无信号, 1:顶背离, -1:底背离
    
    # 检测顶背离(价格上涨但成交量下降)
    top_divergence = (data['price_change'] > 0) & (data['volume_change'] < 0)
    data.loc[top_divergence, 'divergence_signal'] = 1
    
    # 检测底背离(价格下跌但成交量上升)
    bottom_divergence = (data['price_change'] < 0) & (data['volume_change'] > 0)
    data.loc[bottom_divergence, 'divergence_signal'] = -1
    
    return data

def main():
    print("\n股票量价背离分析工具")
    print("="*30)
    
    stock_code = input("请输入要分析的股票代码(如:03690): ").strip()
    if not stock_code:
        print("错误: 股票代码不能为空")
        return
        
    input_file = f"{stock_code}_data.csv"
    output_file = f"{stock_code}_divergence.csv"
    
    try:
        # 读取数据
        data = pd.read_csv(input_file)
        
        # 应用量价背离分析
        result = detect_volume_price_divergence(data)
        
        # 保存结果
        result.to_csv(output_file, index=False)
        print(f"\n量价背离分析完成，结果已保存到{output_file}")
        
    except FileNotFoundError:
        print(f"错误: 找不到数据文件 {input_file}，请先获取该股票数据")
    except Exception as e:
        print(f"分析过程中出错: {e}")

# 主程序
if __name__ == "__main__":
    main()
