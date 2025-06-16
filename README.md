# trade-script
记录我的交易，note my trade information

# Nuclear Power Trade Marker
(中国核电买卖点标记)

This project provides a Pine Script (TradingView) indicator that marks your buy and sell points for 中国核电 (China National Nuclear Power) on the daily candlestick chart, based on your personal trade records.
开始是对自己的资金投资的数据整理和分析，从去年2024年11月开始一直在交易中，但是学习的知识还是不够，无法做到盈利；
现在看了交易的记录，发现几点缺点：

 - 还是交易的策略问题，基本都是情绪主导没有计划；从冲动进场运气好可以盈利，但是慢慢地就还回市场。中国核电就是最好的例子，开始入场就用了10w左右的大仓位（五分之一）买入，第二天到0.2元的盈利就匆忙减仓，后来一直拉起来到10元左右，盈利到近0.5元；可惜没有
## Features

- Marks buy and sell points on the daily chart using your trade data from `核电.csv`
- Displays trade quantity and price at each marker
- Easy to customize for your own trade history

## How to Use

1. **Copy the Pine Script code** from this repository.
2. **Open [TradingView](https://www.tradingview.com/)** and go to the Pine Script editor.
3. **Paste the code** into a new script.
4. **Replace the array.push lines** with your own trade data if needed.
5. **Add the indicator to your daily chart** of 中国核电 (601985).

## Example

The script will show green triangles below bars for buys and red triangles above bars for sells, with quantity and price displayed.

![screenshot](screenshot.png) <!-- If you have a screenshot, put it in your repo and name it screenshot.png -->

## Sample Code Snippet

```pinescript
//@version=6
indicator("中国核电 买卖点标记（含数量和价格）", overlay=true)

var trade_dates   = array.new<int>()
var trade_qtys    = array.new<int>()
var trade_prices  = array.new<float>()

// Example trade data
array.push(trade_dates, timestamp("Asia/Shanghai", 2025, 1, 22, 0, 0))
array.push(trade_qtys, 10700)
array.push(trade_prices, 9.42)
// ... more data ...

// (rest of the script...)
```

## Data Format

Your trade data should be in the format:
- **Date** (YYYY-MM-DD)
- **Quantity** (positive for buy, negative for sell)
- **Price** (trade price)

## License

This project is open source and free to use.

---

**中文说明**

本项目为你在 TradingView 日K线上标记中国核电买卖点的 Pine Script 脚本。  
你可以根据自己的交易记录，自动显示买卖数量和价格。

---
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/lqbin007/trade-script
git push -u origin main
Feel free to improve or translate this README as needed! 
git remote set-url origin https://github.com/lqbin007/trade-script


