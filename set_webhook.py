import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("7666979213:AAESg9nVlPfCkx_lg0gyNUdgoNUFXSbsw0Y")
APP_URL = os.getenv("uzumdehullas-production.up.railway.app")

response = requests.post(
    f"https://api.telegram.org/bot7666979213:AAESg9nVlPfCkx_lg0gyNUdgoNUFXSbsw0Y/setWebhook",
    json={"url": f"https://uzumdehullas-production.up.railway.app/webhook"}
)
print(response.json())
