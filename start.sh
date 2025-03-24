#!/bin/bash

# Set webhook
WEBHOOK_URL="https://uzumdehullas-production.up.railway.app/webhook"
BOT_TOKEN="7666979213:AAESg9nVlPfCkx_lg0gyNUdgoNUFXSbsw0Y"  # Replace with new token!

# Configure webhook
curl -X POST \
  "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "'"${WEBHOOK_URL}"'",
    "allowed_updates": ["message"]
  }'

# Start your application
python main.py
