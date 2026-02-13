# 🦅 A.R.E.S. (Automated Real-time Equity Sentinel)

**A.R.E.S.** is a next-generation financial intelligence platform designed to democratize institutional-grade market analysis. By fusing a **Reactive Web Dashboard** with an **AI-Powered Telegram Bot**, A.R.E.S. delivers real-time insights, automated risk assessments, and generative narratives directly to the investor.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![AI](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-orange)

---

## 🚀 Key Features

### 🧠 Generative AI Analyst (New!)
Powered by **Google Gemini 1.5**, A.R.E.S. doesn't just show numbers; it *thinks*.
- **Narrative Synthesis**: Converts raw technical indicators (RSI, Volatility) and fundamental data (Cash Flow, Debt) into professional, Wall-Street-style executive summaries.
- **Contextual Reasoning**: Understands market sentiment and explains *why* a stock is a Buy or Sell.

### 🌐 Interactive Web Dashboard
- **Real-Time Data**: Live market feeds via Yahoo Finance API.
- **Professional Charting**: Interactive candlesticks, Bollinger Bands, and regression channels using **Plotly**.
- **Self-Service Portal**: Users can manage their own watchlists and trigger instant reports without admin intervention.
- **Privacy-First**: "Stateless" architecture ensures user data is isolated and secure.

### 🤖 The Sentinel Bot (Telegram)
- **24/7 Monitoring**: Always-on surveillance of your portfolio.
- **Commands**:
    - `/price [TICKER]`: Instant snapshot with technical signals.
    - `/analyze [TICKER]`: Deep-dive AI report.
    - `/track [TICKER]`: Add assets to your personal watchlist.
- **Daily Briefing**: A completely automated 09:00 AM pre-market report delivered to your phone.

### ☁️ Cloud-Native & Always-On
- **Serverless Architecture**: Deployed on Streamlit Community Cloud.
- **Zero-Downtime**: Kept alive via external heartbeat monitors (UptimeRobot), ensuring the scheduler runs even when your PC is off.

---

## 🛠️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Generative AI** | **Google Gemini 1.5 Flash** | Narrative generation & synthesis. |
| **Core Logic** | Python 3.x | Backend processing. |
| **Frontend** | Streamlit | Reactive web UI. |
| **Data Engine** | Pandas / NumPy | Vectorized financial calculations. |
| **Market Data** | yfinance | Global & Local (Merval) market feeds. |
| **Bot Framework** | python-telegram-bot | AsyncIO Telegram integration. |
| **Visualization** | Plotly | Interactive financial charts. |
| **Scheduler** | Schedule / Threading | Background automation. |

---

## ⚡ How It Works

1.  **The Brain (Agents)**: A.R.E.S. employs a multi-agent system:
    - **Quant Agent**: Calculates RSI, Beta, Sharpe Ratio.
    - **Researcher Agent**: Digs into balance sheets (Free Cash Flow, Debt).
    - **Synthesizer Agent (AI)**: The Gemini LLM that reads all data and writes the final verdict.

2.  **The Nervous System (Bus)**: Data flows seamlessly between the Cloud Server and the Telegram Bot via a stateless JSON database, ensuring synchronization across all devices.

---

## 📦 Installation & Deployment

### Local Development
```bash
# Clone the repo
git clone https://github.com/your-username/ares-dashboard.git

# Install dependencies
pip install -r requirements.txt

# Configure Secrets
# Create a config.json with your Telegram Token and Gemini API Key

# Run the Sentinel
streamlit run app.py
```

### Cloud Deployment
1.  Fork this repository.
2.  Connect to **Streamlit Community Cloud**.
3.  Add your API Keys (Telegram & Gemini) to the "Secrets" variables.
4.  Deploy! 🚀

---

## 📜 License
This project is open-source and available under the MIT License.

---
*Built with ❤️ by A.R.E.S. Engineering Team*
