from agents.researcher import Researcher

def test_sentiment():
    r = Researcher()
    tickers = ["AAPL", "TSLA", "YPF"]
    
    print("ANALYZING NEWS SENTIMENT\n")
    
    for t in tickers:
        print(f"--- {t} ---")
        result = r.get_sentiment(t)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Sentiment: {result['sentiment']} (Score: {result['polarity']})")
            print("Top Headlines:")
            for h in result['headlines']:
                print(f"  - {h}")
        print("")

if __name__ == "__main__":
    test_sentiment()
