import json
import os

def check_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            data = json.load(f)
            print("Current users.json content:")
            print(json.dumps(data, indent=4))
    else:
        print("users.json does not exist.")

if __name__ == "__main__":
    check_users()
