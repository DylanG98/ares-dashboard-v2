import yfinance as yf
import pandas as pd
import os
from datetime import datetime

def get_market_data(ticker: str, period: str = "2y", save_dir: str = "data/raw") -> pd.DataFrame:
    """
    Fetches OHLCV data for a given ticker from yfinance.
    Implements persistence: Checks for local CSV first before downloading.
    
    Args:
        ticker (str): The stock ticker symbol.
        period (str): The data period to download (default: "2y").
        save_dir (str): Directory to save raw CSVs.
        
    Returns:
        pd.DataFrame: DataFrame containing OHLCV data.
    """
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(save_dir, f"{ticker}_{period}_{today}.csv")
        
        # 1. Check if we already downloaded it today
        if os.path.exists(file_path):
            print(f"Loading data from local cache: {file_path}")
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                # If MultiIndex (Attribute, Ticker), drop the Ticker level
                if isinstance(data.columns, pd.MultiIndex): 
                     data.columns = data.columns.get_level_values(0)
                return data
            except Exception as e:
                print(f"Cache read error: {e}")

    # 2. Download from Yahoo Finance
    print(f"Downloading data for {ticker} from yfinance...")
    try:
        data = yf.download(ticker, period=period, progress=False)
        
        if data.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        # Flatten columns if MultiIndex (Attribute, Ticker)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # 3. Save to CSV (only if save_dir is provided)
        if save_dir:
            data.to_csv(file_path)
            print(f"Data saved to {file_path}")
        
        return data
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()
