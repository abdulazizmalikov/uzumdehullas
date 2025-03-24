import os
import time
import threading
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

class UzumOrderBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.uzum_username = os.getenv('UZUM_USERNAME')
        self.uzum_password = os.getenv('UZUM_PASSWORD')
        self.last_update_id = 0  # For update tracking
        self._start_background_worker()

    def _start_background_worker(self):
        """Start order checking in background"""
        def worker():
            while True:
                self._check_new_orders()
                time.sleep(300)  # Check every 5 minutes

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _check_new_orders(self):
        """Check Uzum for new orders"""
        try:
            # Your existing order checking logic here
            print("Checking for new orders...")
            # orders = get_orders_from_uzum()
            # Process orders...
        except Exception as e:
            print(f"Order check error: {e}")

    # WEBHOOK HANDLERS
    @app.route('/webhook', methods=['POST'])
    def handle_webhook():
        if request.method == 'POST':
            try:
                update = request.json
                print(f"Update received: {update}")

                # Security check
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    if str(chat_id) != os.getenv('TELEGRAM_CHAT_ID'):
                        return jsonify({"status": "unauthorized"}), 403

                    # Handle commands
                    text = update['message'].get('text', '').lower()
                    if '/start' in text:
                        bot.send_telegram_message("🤖 Bot active! Monitoring orders...")
                    elif '/status' in text:
                        bot.send_telegram_message("✅ System operational")

                return jsonify({"status": "ok"}), 200

            except Exception as e:
                print(f"Webhook error: {e}")
                return jsonify({"error": str(e)}), 500

        return jsonify({"status": "method not allowed"}), 405

    def send_telegram_message(self, text):
        """Send message to Telegram"""
        requests.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            json={
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
        )

# Initialize bot
bot = UzumOrderBot()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
