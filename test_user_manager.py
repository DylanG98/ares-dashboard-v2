from utils.user_manager import UserManager
import os

def test_manager():
    print("Testing UserManager...")
    um = UserManager("test_users.json")
    
    # Clean previous
    if os.path.exists("test_users.json"):
        os.remove("test_users.json")
    
    # Test Add
    print("Adding ticker...")
    um.add_ticker("123", "AAPL")
    
    # Test Get
    wl = um.get_watchlist("123")
    print(f"Watchlist: {wl}")
    assert "AAPL" in wl
    
    # Test Remove
    print("Removing ticker...")
    um.remove_ticker("123", "AAPL")
    wl = um.get_watchlist("123")
    print(f"Watchlist: {wl}")
    assert "AAPL" not in wl
    
    print("✅ UserManager logic is valid.")

if __name__ == "__main__":
    test_manager()
