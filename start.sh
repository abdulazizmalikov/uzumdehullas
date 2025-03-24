#!/bin/bash

# Activate Python environment
source /opt/venv/bin/activate

# Set webhook (without jq)
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
  WEBHOOK_URL="https://uzumdehullas-production.up.railway.app/webhook"
  curl -sS -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
    -H "Content-Type: application/json" \
    -d '{"url": "'"${WEBHOOK_URL}"'", "drop_pending_updates": true}' \
    | python3 -c "import sys,json; print('Webhook:', json.load(sys.stdin))" \
    || echo "Webhook setup failed"
  sleep 1
fi

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 main:app
