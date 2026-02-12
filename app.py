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

            # Chart
            if 'Plot Path' in res['quant'] and res['quant']['Plot Path']:
                st.image(res['quant']['Plot Path'], caption=f"{ticker} Technical Analysis", use_column_width=True)

# --- PAGE: BOT MANAGER ---
elif page == "⚙️ Bot Manager":
    st.title("⚙️ Bot Configuration")
    st.markdown("Manage the assets that **A.R.E.S.** watches automatically every day.")
    
    config = load_config()
    watchlist = config.get("watchlist", [])
    
    # Add New Ticker
    c1, c2 = st.columns([3, 1])
    with c1:
        new_ticker = st.text_input("Add Ticker to Watchlist").upper()
    with c2:
        st.write("") # Spacer
        st.write("")
        if st.button("➕ Add"):
            if new_ticker and new_ticker not in watchlist:
                watchlist.append(new_ticker)
                config['watchlist'] = watchlist
                save_config(config)
                st.success(f"Added {new_ticker}")
                st.rerun()
            elif new_ticker in watchlist:
                st.warning("Ticker already in watchlist.")

    st.write("### Current Watchlist")
    
    # Display Watchlist as a grid of removable items
    if watchlist:
        for i in range(0, len(watchlist), 4):
            cols = st.columns(4)
            for j, col in enumerate(cols):
                if i + j < len(watchlist):
                    t = watchlist[i+j]
                    col.write(f"**{t}**")
                    if col.button(f"🗑️ Remove {t}", key=f"del_{t}"):
                        watchlist.remove(t)
                        config['watchlist'] = watchlist
                        save_config(config)
                        st.rerun()
    else:
        st.info("Watchlist is empty.")

    st.divider()
    
    # Telegram Config Display (Read-only for safety)
    # Telegram Config Display & Management
    st.subheader("📢 Telegram Broadcast List")
    
    tg_config = config.get("telegram", {})
    chat_ids = tg_config.get("chat_ids", [])
    
    if isinstance(chat_ids, str):
        chat_ids = [chat_ids]
        
    # Read-Only View for Security
    if chat_ids:
        st.write("Authorized User IDs (Read-Only):")
        for cid in chat_ids:
            st.code(cid)
        st.caption("🔒 To revoke access, edit `Secrets` in Streamlit Cloud dashboard.")
    else:
        st.warning("⚠️ No recipients configured.")
            
    st.divider()

    # User Database View
    st.subheader("👥 User Watchlists (Database)")
    try:
        from utils.user_manager import UserManager
        um = UserManager()
        all_users = um.get_all_users()
        if all_users:
            st.json(all_users)
        else:
            st.info("No personal watchlists active (users are on Global list).")
    except Exception as e:
        st.error(f"Could not load User DB: {e}")
    
    st.divider()
    
    # Token Status
    if config.get("telegram", {}).get("bot_token"):
        st.success("✅ Bot Token Configured")
    else:
        st.error("❌ Bot Token Missing")

# --- BACKGROUND BOT SERVICE ---
@st.cache_resource
def start_bot_background():
    """Starts the Telegram Bot in a separate thread. Singleton via st.cache."""
    try:
        import threading
        from telegram_bot import run_bot_service
        
        # Only start if it's not already running? 
        # st.cache_resource ensures this is called only once per runtime session.
        # But we need to make sure run_bot_service doesn't block the cached function or return immediately.
        # run_bot_service() calls run_polling() which BLOCKS.
        # So we must wrap it in a thread HERE.
        
        bot_thread = threading.Thread(target=run_bot_service, daemon=True)
        bot_thread.start()
        print("✅ Background Bot Thread Started")
        return bot_thread
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        return None

# Start the bot
start_bot_background()
