import yfinance as yf
import pandas as pd

ticker = "YPFD.BA"
print(f"--- Debugging {ticker} ---")

# 1. History
try:
    stock = yf.Ticker(ticker)
    df = stock.history(period="1mo")
    print(f"\n[History] Rows: {len(df)}")
    if not df.empty:
        print(df.head(2))
    else:
        print("History is EMPTY!")
except Exception as e:
    print(f"[History Error] {e}")

# 2. Info (Fundamentals)
try:
    info = stock.info
    print("\n[Info Keys Found]")
    keys_to_check = ['marketCap', 'totalCash', 'totalDebt', 'freeCashflow', 'operatingCashflow']
    for k in keys_to_check:
        val = info.get(k)
        print(f"{k}: {val} (Type: {type(val)})")
        
    print(f"\nCurrency: {info.get('currency', 'N/A')}")
except Exception as e:
    print(f"[Info Error] {e}")

# 3. News
try:
    news = stock.news
    print(f"\n[News] Count: {len(news)}")
    if news:
        print(f"Headline 1: {news[0].get('title')}")
except Exception as e:
    print(f"[News Error] {e}")
