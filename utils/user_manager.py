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
        self.users = self._load_users()

    def _load_users(self):
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            return {}

    def _save_users(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.users, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")

    def get_watchlist(self, user_id: str) -> list:
        """Returns the list of tickers for a specific user."""
        user_id = str(user_id)
        return self.users.get(user_id, [])

    def add_ticker(self, user_id: str, ticker: str) -> bool:
        """Adds a ticker to the user's watchlist. Returns True if added."""
        user_id = str(user_id)
        ticker = ticker.strip().upper()
        
        if user_id not in self.users:
            self.users[user_id] = []
        
        if ticker not in self.users[user_id]:
            self.users[user_id].append(ticker)
            self._save_users()
            return True
        return False

    def remove_ticker(self, user_id: str, ticker: str) -> bool:
        """Removes a ticker from the user's watchlist. Returns True if removed."""
        user_id = str(user_id)
        ticker = ticker.strip().upper()
        
        if user_id in self.users and ticker in self.users[user_id]:
            self.users[user_id].remove(ticker)
            self._save_users()
            return True
        return False
        
    def get_all_users(self) -> dict:
        """Returns the entire user database."""
        return self.users
