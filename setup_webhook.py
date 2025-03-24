import requests
from dotenv import load_dotenv
import os

load_dotenv()

def configure_webhook():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/webhook"
    
    response = requests.post(
        f'https://api.telegram.org/bot{token}/setWebhook',
        json={'url': url}
    )
    
    print("Webhook setup result:", response.json())

if __name__ == "__main__":
    configure_webhook()
