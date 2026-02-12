import time
import os
from agents.quant import QuantEngine
from agents.researcher import Researcher
from agents.synthesizer import Synthesizer
from utils.data_loader import get_market_data
from utils.logger import setup_logger
from utils.notifier import Notifier

logger = setup_logger("SCANNER", "logs")

class MarketScanner:
    def __init__(self):
        self.notifier = Notifier()
        self.config = self.notifier.config
        self.watchlist = self.config.get("watchlist", ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA"])
        
        self.researcher = Researcher()
        self.synthesizer = Synthesizer()

    def scan(self):
        logger.info(f"Starting Market Scan for {len(self.watchlist)} assets...")
        
        for ticker in self.watchlist:
            try:
                self._analyze_ticker(ticker)
            except Exception as e:
                logger.error(f"Failed to analyze {ticker}: {e}")
            
            # Be nice to the API
            time.sleep(1) 
            
        logger.info("Scan complete.")

    def _analyze_ticker(self, ticker):
        logger.info(f"Scanning {ticker}...")
        
        # 1. Get Data
        # We don't save raw CSVs during recurring scans to save space, or we could overwrite
        df = get_market_data(ticker, period="1y", save_dir="data/scanner")
        
        # 2. Researcher (Fast check)
        # In a real scanner, we might cache fundamental data since it doesn't change daily
        intel = self.researcher.get_market_intel(ticker)
        research_data = intel.get("data", {})
        
        # 3. Quant
        quant = QuantEngine(ticker, df, output_dir=f"reports/scanner/{ticker}")
        quant_res = quant.analyze()
        
        if "error" in quant_res:
            logger.warning(f"Quant error for {ticker}: {quant_res['error']}")
            return

        # 4. Synthesize
        signal = self.synthesizer.get_signal(quant_res, research_data)
        verdict = signal['verdict']
        score = signal['score']
        
        logger.info(f"{ticker} -> Verdict: {verdict} (Score: {score})")
        
        # 5. Alert Logic
        # Alert only on STRONG signals
        if "STRONG" in verdict:
            self._send_alert(ticker, verdict, score, signals)

    def _send_alert(self, ticker, verdict, score, reasons):
        icon = "🚀" if "BUY" in verdict else "🔻"
        subject = f"{icon} A.R.E.S. ALERT: {ticker} is a {verdict}!"
        
        body = f"**Asset**: {ticker}\n"
        body += f"**Score**: {score}/2.0\n\n"
        body += "**Reasons:**\n"
        for r in reasons:
            body += f"- {r}\n"
            
        logger.info(f"Triggering alert for {ticker}...")
        self.notifier.send(subject, body)

if __name__ == "__main__":
    scanner = MarketScanner()
    scanner.scan()
