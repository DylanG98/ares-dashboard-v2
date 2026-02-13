import logging
import threading
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from utils.config_loader import load_config
from agents.coordinator import analyze_ticker
from utils.html_generator import HTMLReporter
import os

# Logger setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("TelegramBot")

def get_authorized_ids():
    config = load_config()
    chat_ids = config.get("telegram", {}).get("chat_ids", [])
    # Support migration from single to list
    if not chat_ids and "chat_id" in config.get("telegram", {}):
        chat_ids = [config["telegram"]["chat_id"]]
    # Ensure all are strings
    return [str(cid) for cid in chat_ids]

def is_authorized(update: Update) -> bool:
    user_id = str(update.effective_user.id)
    return user_id in get_authorized_ids()

from utils.user_manager import UserManager

# Initialize User Manager
user_manager = UserManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access.")
        return
    await update.message.reply_text(
        "🤖 **A.R.E.S. 2.0 Online**\n\n"
        "**Market Data:**\n"
        "/price <TICKER> - Snapshot\n"
        "/analyze <TICKER> - Full Report\n\n"
        "**My Watchlist:**\n"
        "/track <TICKER> - Add to favorites\n"
        "/untrack <TICKER> - Remove\n"
        "/watchlist - Show my list",
        parse_mode="Markdown"
    )

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /track <TICKER>")
        return
    
    ticker = context.args[0].upper()
    user_id = str(update.effective_user.id)
    
    if user_manager.add_ticker(user_id, ticker):
        await update.message.reply_text(f"✅ Added **{ticker}** to your watchlist.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"ℹ️ **{ticker}** is already in your watchlist.", parse_mode="Markdown")

async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /untrack <TICKER>")
        return
    
    ticker = context.args[0].upper()
    user_id = str(update.effective_user.id)
    
    if user_manager.remove_ticker(user_id, ticker):
        await update.message.reply_text(f"🗑️ Removed **{ticker}**.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⚠️ **{ticker}** was not found in your watchlist.", parse_mode="Markdown")

async def watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    
    user_id = str(update.effective_user.id)
    # Reload from disk just in case
    user_manager = UserManager()
    tickers = user_manager.get_watchlist(user_id)
    
    if tickers:
        msg = "📋 **Your Watchlist:**\n" + "\n".join([f"- {t}" for t in tickers])
    else:
        msg = "📭 Your watchlist is empty. Use `/track <TICKER>` to add one."
        
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /price <TICKER>")
        return

    ticker = context.args[0].upper()
    status_msg = await update.message.reply_text(f"🔍 Checking {ticker}...")
    
    try:
        # Run in a separate thread to not block the async event loop
        results = await asyncio.to_thread(analyze_ticker, ticker)
        
        if "error" in results:
            await status_msg.edit_text(f"❌ Error: {results['error']}")
            return
            
        quant = results.get("quant", {})
        price = quant.get("Last Price", 0)
        rsi = quant.get("RSI (14)", 0)
        
        # Simple signal
        signal = "HOLD"
        if rsi < 30: signal = "OVERSOLD (Bullish)"
        elif rsi > 70: signal = "OVERBOUGHT (Bearish)"
        
        msg = (
            f"💰 **{ticker} Snapshot**\n"
            f"Price: ${price:.2f}\n"
            f"RSI: {rsi:.2f}\n"
            f"Signal: {signal}"
        )
        await status_msg.edit_text(msg, parse_mode="Markdown")
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: /analyze <TICKER>")
        return

    ticker = context.args[0].upper()
    status_msg = await update.message.reply_text(f"🕵️ Analyzing {ticker}... This may take a minute.")

    try:
        def progress_callback(p, text):
            pass

        results = await asyncio.to_thread(analyze_ticker, ticker, progress_callback)

        if "error" in results:
            await status_msg.edit_text(f"❌ Error: {results['error']}")
            return

        # Generate HTML logic
        report_dir = "temp_dashboard"
        os.makedirs(report_dir, exist_ok=True)
        html_path = os.path.join(report_dir, f"{ticker}_REPORT.html")
        
        reporter = HTMLReporter()
        reporter.generate_report(
            ticker, 
            results['quant'], 
            results['research'], 
            results['report_text'], 
            html_path
        )
        
        # Send Summary Text
        synth = results['synthesis']
        summary = (
            f"📊 **Analysis Complete: {ticker}**\n"
            f"Verdict: {synth['color']} {synth['verdict']}\n"
            f"Confidence: {synth['score']}/3\n\n"
            f"Check the attached report for details."
        )
        
        await status_msg.edit_text(summary, parse_mode="Markdown")
        
        # Send HTML File
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=open(html_path, 'rb'),
            filename=f"{ticker}_ARES_Report.html"
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        await status_msg.edit_text(f"❌ Critical Error during analysis: {str(e)}")


def run_bot_service():
    """Entry point to run the bot."""
    config = load_config()
    token = config.get("telegram", {}).get("bot_token")
    
    if not token or "YOUR_" in token:
        logger.error("Bot token not configured.")
        return

    # Check for existing loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception:
        pass

    application = ApplicationBuilder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("track", track))
    application.add_handler(CommandHandler("untrack", untrack))
    application.add_handler(CommandHandler("watchlist", watchlist))
    
    logger.info("🤖 Telegram Bot Listening...")
    # allowed_updates=Update.ALL_TYPES is good practice
    # stop_signals=None is CRITICAL for running in a background thread (non-main thread)
    application.run_polling(stop_signals=None, close_loop=False)

if __name__ == "__main__":
    run_bot_service()
