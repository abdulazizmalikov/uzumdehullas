#!/bin/bash

# Activate virtual environment
source /opt/venv/bin/activate

# Set webhook (ONLY IF NEEDED)
WEBHOOK_URL="https://uzumdehullas-production.up.railway.app/webhook"
curl -X POST \
  "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "'"$WEBHOOK_URL"'", "drop_pending_updates": true}' \
  || echo "Webhook already set"

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 main:app
