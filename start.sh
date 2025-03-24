#!/bin/bash

# Activate virtual environment
source /opt/venv/bin/activate

# Set webhook (properly formatted)
WEBHOOK_URL="https://uzumdehullas-production.up.railway.app/webhook"
curl -sS -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "'"${WEBHOOK_URL}"'", "drop_pending_updates": true}' \
  && echo "Webhook configured" || echo "Webhook setup failed"

# Start Gunicorn (properly formatted)
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 main:app
