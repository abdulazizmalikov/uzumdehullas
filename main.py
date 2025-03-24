import os
import time
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from storage import OrderStorage

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
        self.storage = OrderStorage()
        self._configure_webhook()

    def _configure_webhook(self):
        """Setup or verify webhook configuration"""
        try:
            # First delete any existing webhook
            requests.post(
                f"https://api.telegram.org/bot{self.token}/deleteWebhook"
            )
            
            # Set new webhook
            webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/webhook"
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/setWebhook",
                json={
                    'url': webhook_url,
                    'allowed_updates': ['message'],
                    'drop_pending_updates': True
                }
            )
            logger.info(f"Webhook configured: {response.json()}")
        except Exception as e:
            logger.error(f"Webhook setup failed: {str(e)}")
            raise

    def verify_chat_id(self, incoming_chat_id):
        """Ensure only authorized chat can interact"""
        return str(incoming_chat_id) == str(self.chat_id)

    def get_auth_token(self):
        """Authenticate with Uzum API"""
        try:
            response = requests.post(
                "https://api-seller.uzum.uz/api/seller/v1/account/token",
                json={
                    "username": self.uzum_username,
                    "password": self.uzum_password
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            logger.error(f"Uzum auth failed: {str(e)}")
            self.send_telegram_message("⚠️ Uzum API authentication failed!")
            raise

    def get_new_orders(self):
        """Fetch orders from Uzum API"""
        try:
            token = self.get_auth_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            last_check = self.storage.get_last_check_time()
            params = {
                'from': int(last_check.timestamp() * 1000),
                'size': 50,
                'sort': 'createdAt,asc'
            }
            
            orders = []
            page = 0
            while True:
                params['page'] = page
                response = requests.get(
                    'https://api-seller.uzum.uz/api/seller/v1/orders',
                    headers=headers,
                    params=params,
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                if not data.get('data'):
                    break
                    
                orders.extend(data['data'])
                page += 1
                
            return orders
        except Exception as e:
            logger.error(f"Order fetch error: {str(e)}")
            self.send_telegram_message("⚠️ Failed to fetch Uzum orders!")
            return []

    def send_telegram_message(self, message):
        """Send message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Telegram send failed: {str(e)}")

    def format_order_message(self, order):
        """Create formatted order notification"""
        created_at = datetime.fromtimestamp(order['createdAt']/1000).strftime('%Y-%m-%d %H:%M:%S')
        items_text = "\n".join([
            f"- {item['productName']} × {item['quantity']} ({item['price']} UZS)"
            for item in order['items']
        ])
        
        return f"""
🛍️ <b>New Uzum Order!</b>

📦 <b>ID:</b> <code>{order['id']}</code>
📅 <b>Date:</b> {created_at}
💰 <b>Total:</b> {order['totalPrice']} UZS
🚚 <b>Method:</b> {order.get('deliveryMethod', 'N/A')}

👤 <b>Customer:</b> {order['customer']['name']}
📞 <b>Phone:</b> {order['customer']['phone']}

📦 <b>Items:</b>
{items_text}

📍 <b>Address:</b> {order.get('deliveryAddress', 'N/A')}
"""

    def run(self):
        """Start the application"""
        @app.route('/webhook', methods=['POST'])
        def webhook_handler():
            try:
                update = request.json
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    if not self.verify_chat_id(chat_id):
                        logger.warning(f"Unauthorized access from {chat_id}")
                        return jsonify({"status": "unauthorized"}), 403
                    
                    if '/start' in update['message'].get('text', ''):
                        self.send_telegram_message("✅ Bot is active and monitoring Uzum orders!")
                
                return jsonify({"status": "ok"}), 200
            except Exception as e:
                logger.error(f"Webhook error: {str(e)}")
                return jsonify({"status": "error"}), 500

        @app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "last_check": self.storage.get_last_check_time().isoformat()
            }), 200

        # Start background order checker
        from threading import Thread
        Thread(target=self._check_orders_loop, daemon=True).start()
        
        return app

    def _check_orders_loop(self):
        """Background order checking loop"""
        while True:
            try:
                logger.info("Checking for new orders...")
                orders = self.get_new_orders()
                
                for order in orders:
                    if not self.storage.is_order_processed(order['id']):
                        message = self.format_order_message(order)
                        self.send_telegram_message(message)
                        self.storage.mark_order_processed(order['id'])
                
                self.storage.update_last_check_time()
                time.sleep(int(os.getenv('CHECK_INTERVAL', 300)))
                
            except Exception as e:
                logger.error(f"Order check error: {str(e)}")
                time.sleep(60)

if __name__ == "__main__":
    try:
        bot = UzumOrderBot()
        app = bot.run()
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
    except Exception as e:
        logger.critical(f"Application failed: {str(e)}")
        raise
