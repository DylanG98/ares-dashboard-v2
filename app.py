import streamlit as st
import pandas as pd
import json
import os
import time

"""
A.R.E.S. Web Dashboard
======================
This is the main entry point for the Streamlit web interface.
It orchestrates the interaction between the user and the autonomous agents:
- QuantEngine: Technical analysis and plotting.
- Researcher: Fundamental data and news sentiment.
- Synthesizer: Final decision making (Buy/Sell/Hold).

Navigation:
- Market Analyzer: Run ad-hoc analysis on any ticker.
- Bot Manager: Manage the watchlist and Telegram recipients.
"""

# A.R.E.S. Components
from utils.config_loader import load_config, save_config

# Page Config
st.set_page_config(
    page_title="A.R.E.S. Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-font { font-size:24px !important; }
    .metric-card {
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

CONFIG_PATH = "config.json"

from agents.coordinator import analyze_ticker

def run_analysis_ui(ticker):
    """Wrapper for analyze_ticker to handle Streamlit UI updates."""
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    def ui_callback(p, text):
        progress_bar.progress(p)
        status_text.text(text)
        
    result = analyze_ticker(ticker, progress_callback=ui_callback)
    
    api_error = result.get("error")
    if api_error:
        status_text.empty()
        progress_bar.empty()
        st.error(f"❌ {api_error}")
        
        # Heuristic hint (kept in UI layer)
        ba_tickers = ["YPFD", "GGAL", "PAMP", "TXAR", "ALUA", "CRES", "EDN", "CEPU", "BMA", "SUPV", "TECO2", "MIRG", "LOMA", "BYMA", "VALO", "CVH"]
        if ticker in ba_tickers:
            st.warning(f"💡 Did you mean **{ticker}.BA**?")
        return None
        
    time.sleep(0.5)
    status_text.empty()
    progress_bar.empty()
    
    return result

# --- SIDEBAR ---
with st.sidebar:
    st.title("🤖 A.R.E.S.")
    st.markdown("Autonomous Research & Equity System")
    st.write("---")
    page = st.radio("Navigation", ["📊 Market Analyzer", "⚙️ Bot Manager"])
    st.write("---")
    st.info("v1.0.0 - Streamlit Edition")

# --- PAGE: MARKET ANALYZER ---
if page == "📊 Market Analyzer":
    st.title("📊 Market Analyzer")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ticker = st.text_input("Ticker Symbol", value="AAPL").upper()
        analyze_btn = st.button("Run Analysis", type="primary")
        
    if analyze_btn:
        res = run_analysis_ui(ticker)
        
        if res:
            # Verdict Section
            verdict = res['synthesis']['verdict']
            color = res['synthesis']['color']
            score = res['synthesis']['score']
            
            st.header(f"{color} Verdict: {verdict}")
            st.metric("Confidence Score", f"{score:.1f} / 3.0")
            
            # Key Signals
            st.subheader("🧠 Rationale")
            for signal in res['synthesis']['signals']:
                st.write(f"- {signal}")
                
            st.divider()
            
            # 3 Columns for Data
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.subheader("📈 Technicals")
                st.metric("Last Price", f"${res['quant'].get('Last Price',0):.2f}")
                st.metric("RSI (14)", f"{res['quant'].get('RSI (14)',0):.2f}")
                st.metric("Volatility", f"{res['quant'].get('Annualized Volatility',0):.1%}")
                
            with c2:
                st.subheader("🏢 Fundamentals")
                st.metric("Market Cap", f"${res['research'].get('Market Cap',0):,.0f}")
                st.metric("Free Cash Flow", f"${res['research'].get('Free Cash Flow',0):,.0f}")
                net_cash = res['research'].get('Cash',0) - res['research'].get('Total Debt',0)
                st.metric("Net Cash", f"${net_cash:,.0f}")
                
            with c3:
                st.subheader("📰 Sentiment (NLP)")
                sent = res['research'].get('sentiment', {})
                st.metric("Polarity Score", f"{sent.get('polarity', 0):.2f}")
                st.caption(f"Mood: {sent.get('sentiment', 'N/A')}")
                
                st.write("**latest Headlines:**")
                for h in sent.get('headlines', []):
                    st.markdown(f"- *{h}*")

            # Chart (Interactive preferred)
            st.subheader("📈 Technical Analysis")
            if 'Interactive Chart' in res['quant']:
                st.plotly_chart(res['quant']['Interactive Chart'], use_container_width=True)
            elif 'Plot Path' in res['quant'] and res['quant']['Plot Path']:
                st.image(res['quant']['Plot Path'], caption=f"{ticker} Technical Analysis", use_column_width=True)

# --- PAGE: BOT MANAGER ---
elif page == "⚙️ Bot Manager":
    st.header("🤖 Bot Configuration")
    
    # Combined "My Watchlist" View (Single Tab)
    st.subheader("👤 My Watchlist & Briefing")
    
    st.info("Enter your Telegram ID to manage your tracking list and trigger reports.")
    
    col_id, col_help = st.columns([2, 1])
    with col_id:
        user_id_input = st.text_input("telegram_id", placeholder="e.g. 12345678", label_visibility="collapsed")
    with col_help:
         st.caption("ℹ️ Send any message to the bot to get your ID.")

    if user_id_input:
        from utils.user_manager import UserManager
        from daily_briefing import MorningBriefing
        
        um = UserManager()
        user_watchlist = um.get_watchlist(user_id_input)
        
        st.divider()
        st.write(f"**WATCHLIST FOR:** `{user_id_input}`")
        
        if user_watchlist:
            st.success(f"Tracking {len(user_watchlist)} assets: " + ", ".join(user_watchlist))
            
            # Management UI
            c1, c2 = st.columns([3, 1])
            with c1:
                ticker_to_remove = st.selectbox("Remove Ticker:", user_watchlist, key="rem_box")
            with c2:
                if st.button("🗑️ Delete"):
                    um.remove_ticker(user_id_input, ticker_to_remove)
                    st.rerun()
        else:
            st.warning("📭 Watchlist is currently empty.")
            
        # Add Ticker Section
        c3, c4 = st.columns([3, 1])
        with c3:
            new_ticker = st.text_input("Add Ticker (Yahoo Symbol):", key="add_box").upper()
        with c4:
             if st.button("➕ Add"):
                if new_ticker:
                    um.add_ticker(user_id_input, new_ticker)
                    st.success(f"Added {new_ticker}")
                    st.rerun()

        st.divider()
        
        # Send Now Button
        st.subheader("🚀 Instant Report")
        if st.button(f"Send Briefing to {user_id_input} Now"):
            with st.spinner("Analyzing markets & generating report..."):
                mb = MorningBriefing()
                # Run for THIS user only
                mb.generate(target_user_id=user_id_input)
            st.success("✅ Report sent! Check your Telegram.")

    st.divider()
    
    # Token Status
    config = load_config()
    if config.get("telegram", {}).get("bot_token"):
        st.success("✅ Bot Token Configured")
    else:
        st.error("❌ Bot Token Missing")

# --- BACKGROUND BOT SERVICE ---
@st.cache_resource
def start_background_services():
    """Starts background threads (Telegram Bot & Scheduler). Singleton."""
    import threading
    import time
    from datetime import datetime
    import schedule
    from telegram_bot import run_bot_service
    from daily_briefing import MorningBriefing
    
    # 1. Telegram Bot Thread
    # Check if already running to prevent duplicates (Conflict error)
    if any(t.name == "TelegramBot" for t in threading.enumerate()):
        print("⚠️ Telegram Bot already running. Skipping start.")
    else:
        try:
            bot_thread = threading.Thread(target=run_bot_service, name="TelegramBot", daemon=True)
            bot_thread.start()
            print("✅ Background Bot Thread Started")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")

    # 2. Scheduler Thread
    def scheduler_loop():
        # Schedule Daily Briefing
        mb = MorningBriefing()
        
        # Schedule at 09:00 AM everyday
        schedule.every().day.at("09:00").do(mb.generate)
        
        # Also run market scan at close? (Optional)
        # schedule.every().day.at("16:30").do(scan_markets...)
        
        print("⏰ Scheduler Started (09:00 AM Briefing)")
        
        while True:
            schedule.run_pending()
            time.sleep(30) # Check every 30s to be more precise

    if any(t.name == "Scheduler" for t in threading.enumerate()):
        print("⚠️ Scheduler already running. Skipping start.")
    else:
        try:
            sched_thread = threading.Thread(target=scheduler_loop, name="Scheduler", daemon=True)
            sched_thread.start()
            print("✅ Background Scheduler Thread Started")
        except Exception as e:
            print(f"❌ Failed to start scheduler: {e}")

# Start Services
start_background_services()
