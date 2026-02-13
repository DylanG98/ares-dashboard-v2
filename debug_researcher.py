import yfinance as yf
import pandas as pd

def debug_ticker(ticker):
    print(f"\n{'='*40}")
    print(f"[DEBUG] TICKER: {ticker}")
    print(f"{'='*40}")
    
    try:
        stock = yf.Ticker(ticker)
        
        # 1. Info Dict Keys
        info = stock.info
        print(f"\n[INFO] keys found: {len(info)}")
        print(f"Sector: {info.get('sector', 'N/A')}")
        print(f"Market Cap: {info.get('marketCap', 'N/A')}")
        
        # Check specific fundamental keys in info
        interest_keys = ['totalDebt', 'totalCash', 'freeCashflow', 'operatingCashflow']
        for k in interest_keys:
            print(f"Info['{k}']: {info.get(k, 'NOT FOUND')}")

        # 2. Balance Sheet
        bs = stock.balance_sheet
        print(f"\n[BALANCE SHEET] Shape: {bs.shape}")
        if not bs.empty:
            print("Row Index (First 10):")
            print(bs.index[:10].tolist())
            
            # Check for specific rows
            target_rows = ['Total Debt', 'Cash And Cash Equivalents', 'Free Cash Flow']
            for row in target_rows:
                if row in bs.index:
                    print(f"Balance Sheet ['{row}']: {bs.loc[row].iloc[0]}")
                else:
                    print(f"Balance Sheet ['{row}']: NOT IN INDEX")
        else:
            print("[WARN] Balance Sheet is EMPTY.")

        # 3. Cash Flow
        cf = stock.cashflow
        print(f"\n[CASH FLOW] Shape: {cf.shape}")
        if not cf.empty:
             print("Row Index (First 10):")
             print(cf.index[:10].tolist())
             
             target_rows = ['Free Cash Flow', 'Operating Cash Flow']
             for row in target_rows:
                if row in cf.index:
                    print(f"Cash Flow ['{row}']: {cf.loc[row].iloc[0]}")
                else:
                    print(f"Cash Flow ['{row}']: NOT IN INDEX")

    except Exception as e:
        print(f"[ERROR]: {e}")

if __name__ == "__main__":
    debug_ticker("AAPL")
    debug_ticker("GGAL.BA")
