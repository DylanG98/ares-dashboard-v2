import yfinance as yf

print("Fetching financials for AAPL...")
ticker = yf.Ticker("AAPL")

try:
    bs = ticker.balance_sheet
    cf = ticker.cashflow
    
    if not bs.empty:
        print("\n--- Balance Sheet (Top 5 rows) ---")
        print(bs.head())
    else:
        print("\nBalance Sheet is empty.")

    if not cf.empty:
        print("\n--- Cash Flow (Top 5 rows) ---")
        print(cf.head())
    else:
        print("\nCash Flow is empty.")
        
except Exception as e:
    print(f"Error: {e}")
