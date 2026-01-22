import json
import os

PENDING_FILE = "pending.json"

def load_pending():
    if not os.path.exists(PENDING_FILE):
        return {"pending": False}
    with open(PENDING_FILE) as f:
        return json.load(f)

def save_pending(data):
    with open(PENDING_FILE, "w") as f:
        json.dump(data, f, indent=2)
