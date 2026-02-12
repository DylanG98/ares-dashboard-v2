import streamlit as st
import pandas as pd
import json
import os
import time

# A.R.E.S. Components
from agents.quant import QuantEngine
from agents.researcher import Researcher
from agents.synthesizer import Synthesizer
from utils.data_loader import get_market_data
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

def run_analysis(ticker):
    """Runs the full A.R.E.S. pipeline for a single ticker."""
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        # 1. Fetch Data
        status_text.text(f"📥 Fetching Market Data for {ticker}...")
        df = get_market_data(ticker, period="2y", save_dir=None) # Don't save CSVs for web runs
        
        if df.empty:
            status_text.empty()
            st.error(f"❌ Could not find data for **{ticker}**.")
            
            # Argentine Ticker Heuristic
            ba_tickers = ["YPFD", "GGAL", "PAMP", "TXAR", "ALUA", "CRES", "EDN", "CEPU", "BMA", "SUPV", "TECO2", "MIRG", "LOMA", "BYMA", "VALO", "CVH"]
            if ticker in ba_tickers:
                st.warning(f"💡 Did you mean **{ticker}.BA**? (Argentine stocks need the .BA suffix)")
            else:
                st.info("Tip: For Buenos Aires stocks, add **.BA** (e.g., YPFD.BA).")
            return None

        progress_bar.progress(25)
        
        # 2. Researcher & NLP
        status_text.text(f"🕵️ Researcher Agent: Analyzing Fundamentals & News...")
        researcher = Researcher()
        intel = researcher.get_market_intel(ticker)
        sentiment = researcher.get_sentiment(ticker)
        intel['data']['sentiment'] = sentiment # Merge
        progress_bar.progress(50)
        
        # 3. Quant
        status_text.text(f"📉 Quant Agent: Calculating Technicals...")
        # Create a temp dir for charts if needed, or handle in-memory.
        # QuantEngine needs an output_dir to save the plot.
        temp_dir = "temp_dashboard"
        os.makedirs(temp_dir, exist_ok=True)
        
        quant = QuantEngine(ticker, df, output_dir=temp_dir)
        quant_res = quant.analyze()
        progress_bar.progress(75)
        
        # 4. Synthesis
        status_text.text(f"⚖️ Synthesizer Agent: Deliberating...")
        synthesizer = Synthesizer()
        report = synthesizer.synthesize(ticker, quant_res, intel['data'])
        analysis = synthesizer.get_signal(quant_res, intel['data'])
        progress_bar.progress(100)
        
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
        return {
            "quant": quant_res,
            "research": intel['data'],
            "synthesis": analysis,
            "report_text": report
        }
        
    except Exception as e:
        status_text.error(f"Error: {str(e)}")
        return None

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
        res = run_analysis(ticker)
        
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
    
    # Ensure it's a list (migration safety)
    if isinstance(chat_ids, str):
        chat_ids = [chat_ids]
        
    c3, c4 = st.columns([3, 1])
    with c3:
        new_chat_id = st.text_input("Add New Chat ID (User ID)")
    with c4:
        st.write("")
        st.write("")
        if st.button("➕ Authorize"):
            if new_chat_id and new_chat_id not in chat_ids:
                chat_ids.append(new_chat_id)
                config['telegram']['chat_ids'] = chat_ids
                # Remove legacy key if exists to avoid confusion
                if 'chat_id' in config['telegram']:
                    del config['telegram']['chat_id']
                save_config(config)
                st.success(f"Authorized ID: {new_chat_id}")
                st.rerun()
            elif new_chat_id in chat_ids:
                st.warning("ID already authorized.")

    if chat_ids:
        st.write("Authorized Users:")
        for i, cid in enumerate(chat_ids):
            col_a, col_b = st.columns([4, 1])
            col_a.code(cid)
            if col_b.button("🗑️ Revoke", key=f"del_id_{cid}"):
                chat_ids.remove(cid)
                config['telegram']['chat_ids'] = chat_ids
                save_config(config)
                st.rerun()
    else:
        st.warning("⚠️ No recipients configured.")
            
    st.divider()
    
    # Token Status
    if config.get("telegram", {}).get("bot_token"):
        st.success("✅ Bot Token Configured")
    else:
        st.error("❌ Bot Token Missing")
