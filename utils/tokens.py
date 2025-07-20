import json
import os
AUTH_FILE = "auth.json"

def save_tokens(data):
    with open(AUTH_FILE, "w") as f:
        json.dump(data, f)

def load_tokens():
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return None
                return json.loads(content)
        except json.JSONDecodeError:
            return None
    return None

def delete_tokens():
    if os.path.exists(AUTH_FILE):
        os.remove(AUTH_FILE)