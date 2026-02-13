import pandas as pd
from datetime import datetime
from utils.data_loader import get_market_data
from utils.notifier import Notifier
from utils.logger import setup_logger

logger = setup_logger("BRIEFING", "logs")

from utils.user_manager import UserManager

class MorningBriefing:
    def __init__(self):
        self.notifier = Notifier()
        self.config = self.notifier.config
        self.user_manager = UserManager()
        self.global_watchlist = self.config.get("watchlist", ["AAPL", "TSLA", "MSFT"])
        
    def _calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _get_market_context(self):
        """Fetches SPY data once for all reports."""
        try:
            spy_df = get_market_data("SPY", period="6mo", save_dir="data/briefing")
            spy_close = spy_df['Close'].iloc[-1]
            spy_prev = spy_df['Close'].iloc[-2]
            spy_chg = ((spy_close - spy_prev) / spy_prev) * 100
            market_icon = "🟢" if spy_chg >= 0 else "🔴"
            return f"🌍 *Mercado (SPY)*: ${spy_close:.2f} ({market_icon} {spy_chg:+.2f}%)\n\n"
        except Exception as e:
            logger.error(f"Error fetching SPY: {e}")
            return "🌍 *Mercado (SPY)*: N/A\n\n"

    def _build_report(self, context_str, watchlist, title_suffix=""):
        today_str = datetime.now().strftime("%d-%b")
        message = f"☀️ *A.R.E.S. Briefing ({today_str})* {title_suffix}\n\n"
        message += context_str
        
        # Split Watchlist
        us_tickers = [t for t in watchlist if ".BA" not in t]
        arg_tickers = [t for t in watchlist if ".BA" in t]
        
        message += self._build_table("🇺🇸 *Wall Street*", us_tickers)
        message += self._build_table("🇦🇷 *Merval*", arg_tickers)
        
        return message

    def _build_table(self, title, tickers):
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
                
                close_val = float(close)
                change_val = float(change_pct)
                
                disp_ticker = ticker.replace(".BA", "") if ".BA" in ticker else ticker
                
                t_str = f"{disp_ticker:<6}"
                p_str = f"${close_val:<7.2f}"
                c_str = f"{change_val:+.1f}%"
                
                row = f"`| {t_str} | {p_str} | {c_str:<5} | {rsi_str:<3} |`"
                t_msg += row + "\n"
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
        return t_msg

    def generate(self, target_user_id=None):
        logger.info(f"Generating personalized briefings... Target: {target_user_id if target_user_id else 'ALL'}")
        
        # 1. Get Authorized Users
        tg_conf = self.config.get("telegram", {})
        
        if target_user_id:
             # If targeting a specific user, we don't need to check config allowlist, 
             # assuming the caller (app.py) verified it or it's a manual test.
             # Converting to string to ensure matching
             authorized_users = [str(target_user_id)]
        else:
            chat_ids = tg_conf.get("chat_ids", [])
            if not chat_ids and "chat_id" in tg_conf:
                chat_ids = [tg_conf["chat_id"]]
            authorized_users = [str(uid) for uid in chat_ids]
        
        if not authorized_users:
            logger.warning("No users to send briefing to.")
            return

        # 2. Market Context (calc once)
        spy_context = self._get_market_context()
        
        # 3. Iterate and Send
        for user_id in authorized_users:
            user_watchlist = self.user_manager.get_watchlist(user_id)
            
            if user_watchlist:
                watchlist = user_watchlist
                mode = "Personal"
            else:
                watchlist = self.global_watchlist
                mode = "Global"
                
            logger.info(f"Preparing briefing for {user_id} ({mode})...")
            report = self._build_report(spy_context, watchlist, title_suffix="")
            
            if self.notifier.send_telegram(report, target_chat_id=user_id):
                logger.info(f"Sent to {user_id}")
            else:
                logger.error(f"Failed to send to {user_id}")
                
        logger.info("Briefing cycle complete.")

if __name__ == "__main__":
    mb = MorningBriefing()
    mb.generate()
