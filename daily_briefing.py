import pandas as pd
from datetime import datetime
from utils.data_loader import get_market_data
from utils.notifier import Notifier
from utils.logger import setup_logger

logger = setup_logger("BRIEFING", "logs")

class MorningBriefing:
    def __init__(self):
        self.notifier = Notifier()
        self.config = self.notifier.config
        self.watchlist = self.config.get("watchlist", ["AAPL", "TSLA", "MSFT"])
        
    def _calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate(self):
        logger.info("Generating Morning Briefing...")
        today_str = datetime.now().strftime("%d-%b")
        
        # 1. Market Context (SPY)
        try:
            spy_df = get_market_data("SPY", period="6mo", save_dir="data/briefing")
            spy_close = spy_df['Close'].iloc[-1]
            spy_prev = spy_df['Close'].iloc[-2]
            spy_chg = ((spy_close - spy_prev) / spy_prev) * 100
            market_icon = "🟢" if spy_chg >= 0 else "🔴"
            
            message = f"☀️ *A.R.E.S. Morning Briefing ({today_str})*\n\n"
            message += f"🌍 *Mercado (SPY)*: ${spy_close:.2f} ({market_icon} {spy_chg:+.2f}%)\n\n"
        except Exception as e:
            logger.error(f"Error fetching SPY: {e}")
            message = f"☀️ *A.R.E.S. Morning Briefing ({today_str})*\n\n"
            message += "🌍 *Mercado (SPY)*: N/A\n\n"

        # 2. Watchlist Tables
        
        # Split Watchlist
        us_tickers = [t for t in self.watchlist if ".BA" not in t]
        arg_tickers = [t for t in self.watchlist if ".BA" in t]
        
        # Helper to generate table
        def build_table(title, tickers):
            if not tickers: return ""
            t_msg = f"\n{title}\n"
            t_msg += "`| Ticker | Precio  | Var % | RSI |`\n"
            t_msg += "`| :--- | :--- | :--- | :--- |`\n"
            
            for ticker in tickers:
                try:
                    df = get_market_data(ticker, period="6mo", save_dir="data/briefing")
                    if df.empty: continue
                    
                    close = df['Close'].iloc[-1]
                    prev = df['Close'].iloc[-2]
                    change_pct = ((close - prev) / prev) * 100
                    
                    # RSI Calculation
                    rsi_series = self._calculate_rsi(df['Close'])
                    rsi = rsi_series.iloc[-1]
                    
                    # Formatting
                    rsi_str = f"{rsi:.0f}"
                    if rsi > 70: rsi_str += "🔥"
                    if rsi < 30: rsi_str += "❄️"
                    
                    # Formatting scalars
                    close_val = float(close)
                    change_val = float(change_pct)
                    
                    # Ticker clean up for display (remove .BA for cleaner look if desired, but keep for clarity)
                    disp_ticker = ticker.replace(".BA", "") if ".BA" in ticker else ticker
                    
                    t_str = f"{disp_ticker:<6}"
                    p_str = f"${close_val:<7.2f}"
                    c_str = f"{change_val:+.1f}%"
                    
                    row = f"`| {t_str} | {p_str} | {c_str:<5} | {rsi_str:<3} |`"
                    t_msg += row + "\n"
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {e}")
            return t_msg

        message += build_table("🇺🇸 *Wall Street*", us_tickers)
        message += build_table("🇦🇷 *Merval (Argentina)*", arg_tickers)
                
        # 3. Send
        logger.info("Sending briefing...")
        self.notifier.send_telegram(message)
        logger.info("Briefing sent.")

if __name__ == "__main__":
    mb = MorningBriefing()
    mb.generate()
