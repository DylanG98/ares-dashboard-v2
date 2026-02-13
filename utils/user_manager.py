import json
import os
import logging

logger = logging.getLogger("UserManager")

USERS_FILE = "users.json"

class UserManager:
    """
    Manages user-specific watchlists.
    Data Structure: { "USER_ID": ["TICKER1", "TICKER2"] }
    """
    def __init__(self, filepath=USERS_FILE):
        self.filepath = filepath

    def _load_users(self):
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            return {}

    def _save_users(self, users):
        try:
            with open(self.filepath, "w") as f:
                json.dump(users, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")

    def get_watchlist(self, user_id: str) -> list:
        """Returns the list of tickers for a specific user."""
        users = self._load_users()
        user_id = str(user_id)
        return users.get(user_id, [])

    def add_ticker(self, user_id: str, ticker: str) -> bool:
        """Adds a ticker to the user's watchlist. Returns True if added."""
        users = self._load_users()
        user_id = str(user_id)
        ticker = ticker.strip().upper()
        
        if user_id not in users:
            users[user_id] = []
        
        if ticker not in users[user_id]:
            users[user_id].append(ticker)
            self._save_users(users)
            return True
        return False

    def remove_ticker(self, user_id: str, ticker: str) -> bool:
        """Removes a ticker from the user's watchlist. Returns True if removed."""
        users = self._load_users()
        user_id = str(user_id)
        ticker = ticker.strip().upper()
        
        if user_id in users and ticker in users[user_id]:
            users[user_id].remove(ticker)
            self._save_users(users)
            return True
        return False
        
    def get_all_users(self) -> dict:
        """Returns the entire user database."""
        return self._load_users()
