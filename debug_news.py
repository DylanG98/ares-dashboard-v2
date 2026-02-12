import yfinance as yf
import json

def debug_news():
    ticker = "AAPL"
    print(f"Fetching news for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        print(f"Type of news: {type(news)}")
        print(f"Length of news: {len(news)}")
        if news:
            print("First item keys:", news[0].keys())
            print(json.dumps(news[0], indent=2))
        else:
            print("News list is empty.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_news()
