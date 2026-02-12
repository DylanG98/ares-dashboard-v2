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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access.")
        return
    await update.message.reply_text(
        "🤖 **A.R.E.S. Online**\n\n"
        "Commands:\n"
        "/price <TICKER> - Fast snapshot\n"
        "/analyze <TICKER> - Full Report (HTML)\n"
        "/help - Show this menu",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /price <TICKER>")
        return

    ticker = context.args[0].upper()
    status_msg = await update.message.reply_text(f"🔍 Checking {ticker}...")
    
    # We use a partial run or just the coordinator but only return price? 
    # For speed, we can just use the coordinator and extract what we need.
    # Ideally we'd have a lighter function, but analyze_ticker is robust.
    # Let's use analyze_ticker but suppress the slow sentiment if possible?
    # For now, full analysis is fine, or we can just fetch data directly.
    # To keep it "Fast", let's just use the Coordinator which is consistent.
    
    try:
        # Run in a separate thread to not block the async event loop
        # But analyze_ticker is synchronous.
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
        # Define a callback to update the telegram message with progress? 
        # Updating too often triggers rate limits. Let's just update once or twice.
        def progress_callback(p, text):
            # Only update on key milestones to avoid spam/rate limit
            if p in [30, 60, 90]: 
                # asyncio.run_coroutine_threadsafe(status_msg.edit_text(f"⏳ {ticker}: {text}"), loop)
                # It's hard to mix sync callback with async telegram methods here without the loop.
                # We'll skip granular updates for now.
                pass

        results = await asyncio.to_thread(analyze_ticker, ticker, progress_callback)

        if "error" in results:
            await status_msg.edit_text(f"❌ Error: {results['error']}")
            return

        # Generate HTML logic
        # We need to save the HTML to send it.
        # Use temp dir
        report_dir = "temp_dashboard"
        os.makedirs(report_dir, exist_ok=True)
        html_path = os.path.join(report_dir, f"{ticker}_REPORT.html")
        
        reporter = HTMLReporter()
        # Synthesis report text is markdown, needed for HTML?
        # The HTMLReporter expects: ticker, quant_data, fundamental_data, synthesis_text, output_path
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
    
    logger.info("🤖 Telegram Bot Listening...")
    # allowed_updates=Update.ALL_TYPES is good practice
    # stop_signals=None is CRITICAL for running in a background thread (non-main thread)
    application.run_polling(stop_signals=None, close_loop=False)

if __name__ == "__main__":
    run_bot_service()
