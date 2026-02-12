from utils.notifier import Notifier
import sys

def test():
    print("Testing Telegram Connection...")
    n = Notifier()
    success = n.send_telegram("🔔 *A.R.E.S. SYSTEM ONLINE* 🔔\n\nConnection established successfully.\nMonitoring active.")
    
    if success:
        print("✅ Message Sent Successfully!")
    else:
        print("❌ Message Failed. Check logs/notifier.py.log")

if __name__ == "__main__":
    test()
