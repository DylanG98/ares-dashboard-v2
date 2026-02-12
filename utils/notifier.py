import requests
import json
import os
from utils.logger import setup_logger
from utils.config_loader import load_config

logger = setup_logger("NOTIFIER")

class Notifier:
    def __init__(self, config_path="config.json"):
        self.config = load_config(config_path)

    def send_telegram(self, message, target_chat_id=None):
        tg_conf = self.config.get("telegram", {})
        token = tg_conf.get("bot_token")
        
        # Determine recipients: specific target OR all authorized in config
        if target_chat_id:
            chat_ids = [target_chat_id]
        else:
            # Broadcast to all
            chat_ids = tg_conf.get("chat_ids", [])
            if not chat_ids and "chat_id" in tg_conf:
                chat_ids = [tg_conf["chat_id"]]

        if not token or not chat_ids or "YOUR_" in token:
            logger.warning("Telegram credentials not configured.")
            return False
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        success_count = 0
        for chat_id in chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    success_count += 1
                else:
                    logger.error(f"Telegram failed for {chat_id}: {response.text}")
            except Exception as e:
                logger.error(f"Telegram connection error for {chat_id}: {e}")
        
        if success_count > 0:
            logger.info(f"Telegram notification sent to {success_count} recipients.")
            return True
        return False

    def send(self, subject, body):
        """
        Generic send method for all enabled channels.
        """
        # Format message for Telegram (Subject in bold)
        tg_message = f"*{subject}*\n\n{body}"
        self.send_telegram(tg_message)
        
        # Email logic can be added here if enabled in config
