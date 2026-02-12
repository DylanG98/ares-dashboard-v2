import pandas as pd
import numpy as np
import os
import sys
from agents.quant import QuantEngine
from agents.synthesizer import Synthesizer
from agents.researcher import Researcher
from utils.data_loader import get_market_data
from utils.logger import setup_logger

logger = setup_logger("BACKTEST", "logs")

class BacktestEngine:
    def __init__(self, ticker, initial_capital=10000):
        self.ticker = ticker
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.shares = 0
        self.portfolio_history = []
        self.trade_log = []
        
        # Load Data (Defaults to 2y for backtest speed)
        # Using save_dir="data/raw" to leverage existing cache
        self.data = get_market_data(ticker, period="5y", save_dir=os.path.join("data", "raw"))
        
        # Pre-calc indicators
        # We instantiate a dummy Researcher to get static data for the simulation (Limitation of MVP)
        # Ideally we would have historical fundamental data.
        try:
            self.researcher = Researcher()
            intel = self.researcher.get_market_intel(ticker)
            self.research_data = intel.get("data", {})
        except Exception as e:
            logger.error(f"Failed to fetch fundamental data: {e}")
            self.research_data = {}
        
        # Run Quant analysis to populate indicators in DataFrame
        self.quant = QuantEngine(ticker, self.data)
        self.quant.analyze() 
        # Now self.data has columns like 'RSI_14'
        
        self.synthesizer = Synthesizer()

    def run(self):
        if self.data.empty:
            logger.error("No data to backtest.")
            return

        logger.info(f"Starting Backtest for {self.ticker} over {len(self.data)} days...")
        
        # Iterate row by row to simulate time passing
        for date, row in self.data.iterrows():
            price = row['Close']
            
            # Construct mock quant result for this day
            # We only extract what the Synthesizer needs for decision making
            rsi = row.get('RSI_14', 50)
            if pd.isna(rsi): rsi = 50
            
            quant_data = {
                "RSI (14)": rsi,
                # Volatility is not used for SCORING in Synthesizer, so we can omit or pass 0
                "Annualized Volatility": 0, 
            }
            
            # Get Signal from Synthesizer
            signal = self.synthesizer.get_signal(quant_data, self.research_data)
            score = signal['score']
            verdict = signal['verdict']
            
            # Execute Strategy
            self._execute_trade(date, price, score, verdict)
            
            # Track Performance
            total_value = self.capital + (self.shares * price)
            self.portfolio_history.append({
                "Date": date,
                "Portfolio Value": total_value,
                "Price": price
            })
            
        self._generate_report()

    def _execute_trade(self, date, price, score, verdict):
        # Strategy Logic matching Synthesizer verdicts:
        # STRONG BUY or BUY (Score >= 0.5) -> Buy
        # STRONG SELL or SELL (Score <= -0.5) -> Sell
        
        if score >= 0.5:
            # BUY SIGNAL
            # If we have capital, buy.
            if self.capital > price:
                num_shares = int(self.capital // price)
                if num_shares > 0:
                    cost = num_shares * price
                    self.capital -= cost
                    self.shares += num_shares
                    self.trade_log.append(f"{date.date()}: BUY {num_shares} @ ${price:.2f} (Verdict: {verdict})")
        
        elif score <= -0.5:
            # SELL SIGNAL
            # If we have shares, sell all.
            if self.shares > 0:
                revenue = self.shares * price
                self.capital += revenue
                self.trade_log.append(f"{date.date()}: SELL {self.shares} @ ${price:.2f} (Verdict: {verdict})")
                self.shares = 0

    def _generate_report(self):
        if not self.portfolio_history:
            logger.warning("No data to report.")
            return

        df = pd.DataFrame(self.portfolio_history).set_index("Date")
        
        initial = self.initial_capital
        final = df.iloc[-1]["Portfolio Value"]
        roi = ((final - initial) / initial) * 100
        
        # Buy & Hold Comparison
        initial_price = df.iloc[0]["Price"]
        final_price = df.iloc[-1]["Price"]
        bh_roi = ((final_price - initial_price) / initial_price) * 100
        
        logger.info("="*60)
        logger.info(f"BACKTEST RESULTS: {self.ticker}")
        logger.info("="*60)
        logger.info(f"Duration:        {df.index[0].date()} to {df.index[-1].date()}")
        logger.info(f"Initial Capital: ${initial:,.2f}")
        logger.info(f"Final Value:     ${final:,.2f}")
        logger.info(f"Strategy ROI:    {roi:.2f}%")
        logger.info(f"Buy & Hold ROI:  {bh_roi:.2f}%")
        logger.info(f"Total Trades:    {len(self.trade_log)}")
        
        if roi > bh_roi:
            logger.info("RESULT: Strategy BEATS Buy & Hold!")
        else:
            logger.info("RESULT: Strategy UNDERPERFORMED Buy & Hold.")
            
        logger.info("-" * 20)
        logger.info("Last 5 Trades:")
        for trade in self.trade_log[-5:]:
            logger.info(trade)
        logger.info("="*60)

if __name__ == "__main__":
    target = sys.argv[1].upper() if len(sys.argv) > 1 else "AAPL"
    try:
        engine = BacktestEngine(target)
        engine.run()
    except Exception as e:
        logger.critical(f"Backtest crashed: {e}")
