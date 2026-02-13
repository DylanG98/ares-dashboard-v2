from agents.synthesizer import Synthesizer
import google.generativeai as genai
import os
import sys

# Force UTF-8 for Windows Console
sys.stdout.reconfigure(encoding='utf-8')

def test_ai():
    print("[TEST] Testing Gemini AI Integration...")
    
    # 1. List Models to debug 404
    api_key = "AIzaSyAJAOTsiXuqS4yJHYEFbws-XIdNZDh_uaM" # Hardcoded for test
    genai.configure(api_key=api_key)
    try:
        print("\n--- Available Models ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    synth = Synthesizer()
    
    # Mock Data for AAPL
    ticker = "AAPL"
    quant_data = {
        "RSI (14)": 35.5,
        "Annualized Volatility": 0.22,
        "Beta": 1.1,
        "Sharpe Ratio": 1.5
    }
    researcher_data = {
        "Free Cash Flow": 100000000000,
        "Total Debt": 50000000000,
        "Cash": 60000000000,
        "Market Cap": 3000000000000,
        "sentiment": {"sentiment": "Bullish", "polarity": 0.25}
    }
    
    print("\n--- Sending Data to Gemini ---")
    try:
        report = synth.synthesize(ticker, quant_data, researcher_data)
        print("\n[SUCCESS] AI Report Result:")
        print("="*50)
        print(report)
        print("="*50)
    except Exception as e:
        print(f"[ERROR] AI Synthesis failed: {e}")

    print("\n--- Testing Legacy get_signal ---")
    try:
        signals = synth.get_signal(quant_data, researcher_data)
        print(f"[SUCCESS] Verdict: {signals['verdict']} | Score: {signals['score']}")
    except Exception as e:
        print(f"[ERROR] get_signal failed: {e}")

if __name__ == "__main__":
    test_ai()
