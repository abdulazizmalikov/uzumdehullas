# Uzum Market Telegram Bot

Get instant Telegram notifications when you receive new orders on Uzum Market.

## Features
- Real-time order notifications via webhook
- Exclusive access for your chat ID only
- Order history tracking
- Health monitoring endpoint

## Setup
1. Clone this repository
2. Create `.env` file from `.env.example`
3. Fill in your credentials
4. Deploy to Railway

## Deployment
1. Create new Railway project
2. Connect your GitHub repository
3. Add all environment variables
4. Deploy!

## Commands
- `/start` - Verify bot is working
- Health check: `https://your-app.up.railway.app/health`

## Webhook Setup
After deployment, run:
```bash
python setup_webhook.py
