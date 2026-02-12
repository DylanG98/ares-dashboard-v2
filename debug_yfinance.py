import yfinance as yf
import pandas as pd

def debug_ticker(ticker):
    print(f"--- Debugging {ticker} ---")
    try:
        stock = yf.Ticker(ticker)
        
        # 1. Info Keys
        print("\n[INFO KEYS related to Cash/Debt/MarketCap]")
        info = stock.info
        keys_to_check = [k for k in info.keys() if any(x in k.lower() for x in ['cash', 'debt', 'cap', 'free'])]
        for k in keys_to_check:
            print(f"{k}: {info[k]}")

        # 2. Fast Info
        print("\n[FAST INFO]")
        try:
            print(f"Market Cap: {stock.fast_info['market_cap']}")
        except:
            print("Fast info market_cap not found")

        # 3. Cashflow
        print("\n[CASH FLOW COLUMNS/INDEX]")
        cf = stock.cashflow
        if not cf.empty:
            print(cf.index.tolist())
            print(cf.head())
        else:
            print("Cashflow empty")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_ticker("AAPL")
    debug_ticker("YPF") # Try a different one too
