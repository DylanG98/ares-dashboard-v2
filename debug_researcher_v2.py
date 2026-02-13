from agents.researcher import Researcher

def test_ticker(ticker):
    print(f"\n{'='*40}")
    print(f"Testing {ticker} with ACTUAL Researcher Class")
    print(f"{'='*40}")
    
    r = Researcher()
    intel = r.get_market_intel(ticker)
    
    print("\n--- REPORT ---")
    print(intel['report'])
    
    print("\n--- DATA ---")
    print(intel['data'])

if __name__ == "__main__":
    test_ticker("AAPL")
    test_ticker("GGAL.BA")
    test_ticker("YPFD.BA")
