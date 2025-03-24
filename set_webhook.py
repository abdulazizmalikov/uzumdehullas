import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get values from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Store in .env file!
APP_URL = os.getenv("RAILWAY_STATIC_URL")

# Configure webhook
response = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    json={
        "url": f"https://{APP_URL}/webhook",
        "allowed_updates": ["message"]
    }
)

print("Webhook setup result:", response.json())
