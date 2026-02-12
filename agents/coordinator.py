import os
import time
from agents.quant import QuantEngine
from agents.researcher import Researcher
from agents.synthesizer import Synthesizer
from utils.data_loader import get_market_data

def analyze_ticker(ticker, progress_callback=None):
    """
    Orchestrates the full A.R.E.S. pipeline for a single ticker.
    Shared logic for Streamlit App and Telegram Bot.
    
    Args:
        ticker (str): The stock ticker symbol.
        progress_callback (callable, optional): Function (percent, status_text) -> None.
        
    Returns:
        dict: {
            "quant": dict,
            "research": dict,
            "synthesis": dict,
            "report_text": str,
            "error": str (optional)
        }
    """
    def update_progress(p, text):
        if progress_callback:
            progress_callback(p, text)

    try:
        # 1. Fetch Data
        update_progress(10, f"📥 Fetching Market Data for {ticker}...")
        df = get_market_data(ticker, period="2y", save_dir=None)
        
        if df.empty:
            return {"error": f"Could not find data for {ticker}. Check spelling or add .BA for Argentina."}

        # 2. Researcher & NLP
        update_progress(30, f"🕵️ Researcher Agent: Analyzing Fundamentals & News...")
        researcher = Researcher()
        intel = researcher.get_market_intel(ticker)
        sentiment = researcher.get_sentiment(ticker)
        intel['data']['sentiment'] = sentiment # Merge
        
        # 3. Quant
        update_progress(60, f"📉 Quant Agent: Calculating Technicals...")
        # Temp dir for plots
        temp_dir = "temp_dashboard"
        os.makedirs(temp_dir, exist_ok=True)
        
        quant = QuantEngine(ticker, df, output_dir=temp_dir)
        quant_res = quant.analyze()
        
        # 4. Synthesis
        update_progress(80, f"⚖️ Synthesizer Agent: Deliberating...")
        synthesizer = Synthesizer()
        report = synthesizer.synthesize(ticker, quant_res, intel['data'])
        analysis = synthesizer.get_signal(quant_res, intel['data'])
        
        update_progress(100, "✅ Analysis Complete.")
        
        return {
            "quant": quant_res,
            "research": intel['data'],
            "synthesis": analysis,
            "report_text": report
        }
        
    except Exception as e:
        return {"error": str(e)}
