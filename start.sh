#!/bin/bash

# Activate Python virtual environment
source /opt/venv/bin/activate

# Set webhook on startup
python -c "
import os, requests; 
requests.post(
    f'https://api.telegram.org/bot{os.getenv(\"TELEGRAM_BOT_TOKEN\")}/setWebhook',
    json={
        'url': f'https://{os.getenv(\"RAILWAY_STATIC_URL\")}/webhook',
        'allowed_updates': ['message'],
        'drop_pending_updates': True
    }
)
"

# Start the application
gunicorn --bind 0.0.0.0:$PORT --timeout 600 main:app
