import os
import time
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

class UzumOrderBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.uzum_username = os.getenv('UZUM_USERNAME')
        self.uzum_password = os.getenv('UZUM_PASSWORD')
        self.last_request = time.time()
        
        # Debug env vars
        logger.info("Environment Variables Loaded:")
        logger.info(f"BOT_TOKEN: {'*****' if self.token else 'MISSING'}")
        logger.info(f"CHAT_ID: {self.chat_id or 'MISSING'}")
        
        self._start_background_worker()

    def _start_background_worker(self):
        """Start order checking in background"""
        def worker():
            while True:
                try:
                    self._check_new_orders()
                except Exception as e:
                    logger.error(f"Background worker error: {str(e)}")
                time.sleep(300)  # 5 minutes

        threading.Thread(target=worker, daemon=True).start()

    # ... [Include your existing Uzum API methods here] ...

    @app.route('/webhook', methods=['POST'])
    def handle_webhook():
        try:
            # Enhanced request logging
            logger.info("\n" + "="*50)
            logger.info("Incoming Headers: %s", dict(request.headers))
            
            if not request.is_json:
                logger.error("Non-JSON request received")
                return jsonify({"error": "JSON required"}), 400

            update = request.get_json()
            logger.info("Raw Update: %s", update)

            # Security check
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                if str(chat_id) != os.getenv('TELEGRAM_CHAT_ID'):
                    logger.warning(f"Unauthorized access from: {chat_id}")
                    return jsonify({"status": "unauthorized"}), 403

                # Command handling
                text = update['message'].get('text', '').lower()
                if '/start' in text:
                    bot.send_telegram_message("🔄 Bot activated!")
                elif '/status' in text:
                    bot.send_telegram_message("✅ System operational")

            return jsonify({"status": "success"}), 200

        except Exception as e:
            logger.error(f"Webhook failed: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal error"}), 500

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }), 200

    def send_telegram_message(self, text):
        """Safe message sending with rate limiting"""
        try:
            now = time.time()
            if now - self.last_request < 1:
                time.sleep(1)
                
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={
                    'chat_id': self.chat_id,
                    'text': text,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            response.raise_for_status()
            self.last_request = time.time()
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")

# Initialize bot
bot = UzumOrderBot()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
