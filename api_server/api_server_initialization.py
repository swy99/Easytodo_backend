import json
import os


def init_google_oauth():
    with open('google.json', 'r') as f:
        goauth = json.load(f)
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", goauth["web"]["client_id"])
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", goauth["web"]["client_secret"])
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    return GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL