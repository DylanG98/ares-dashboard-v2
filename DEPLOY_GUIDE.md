# ☁️ A.R.E.S. Cloud Deployment Guide

This guide will help you deploy your A.R.E.S. Dashboard to **Streamlit Community Cloud** (Free) so you can access it from anywhere (Phone, Laptop, etc).

## ⚠️ Important Considerations
1.  **Public vs Private**: Streamlit Cloud is free for public repositories. For private data, ensure you don't commit `config.json` with real passwords to GitHub.
2.  **Ephemeral File System**: The cloud resets every time you reboot the app. Changes made via "Bot Manager" (adding tickers) **will not persist** permanently in the cloud version (unless you connect a database, which is advanced).
    *   *Solution*: Configure your "Master Watchlist" in the Code (`config.json` inside GitHub) before deploying.

## Step 1: Prepare for GitHub
1.  **Create a GitHub Account** if you don't have one: [github.com](https://github.com/)
2.  **Create a New Repository**:
    *   Name: `ares-dashboard`
    *   Public (Free) or Private.
3.  **Upload your Files**:
    *   You need to upload all `.py` files, `requirements.txt`, and folders (`agents/`, `utils/`).
    *   **DO NOT UPLOAD**: `config.json` (if it has real passwords). We will use "Secrets" instead.

## Step 2: Connect to Streamlit
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Login with GitHub.
3.  Click **"New App"**.
4.  Select your Repository (`ares-dashboard`).
5.  Main file path: `app.py`.

## Step 3: Configure Secrets (Crucial!)
Since we didn't upload `config.json` (for security), we must give the cloud our passwords securley.

1.  In the Streamlit Deploy screen, click **"Advanced Settings"**.
2.  Find the **"Secrets"** box.
3.  Paste your configuration in TOML format (like this):

```toml
[telegram]
bot_token = "YOUR_BOT_TOKEN_HERE"
chat_ids = ["12345678", "87654321"]

[email]
enabled = false

# Watchlist must be a standard list
watchlist = ["AAPL", "TSLA", "NVDA", "YPFD.BA"]
```

4.  Click **Save**.

## Step 4: Launch 🚀
1.  Click **"Deploy!"**.
2.  Wait 1-2 minutes while it installs libraries.
3.  **Done!** You will get a URL like `https://ares-dashboard.streamlit.app` to share.

## Troubleshooting
*   **"ModuleNotFoundError"**: Check if `requirements.txt` includes all libraries (pandas, yfinance, etc).
*   **"KeyError: telegram"**: You forgot to set the Secrets in Step 3.
