import os
import time
import logging
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from storage import OrderStorage

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

class UzumOrderBot:
    def __init__(self):
        self.token = os.getenv('7666979213:AAESg9nVlPfCkx_lg0gyNUdgoNUFXSbsw0Y')
        self.chat_id = os.getenv('998980322')
        self.uzum_username = os.getenv('abdulazizchik@icloud.com')
        self.uzum_password = os.getenv('ZEZ1999M')
        self.storage = OrderStorage()
        self._setup_webhook()

    def _setup_webhook(self):
        webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/webhook"
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/setWebhook",
                json={"url": webhook_url}
            )
            logger.info(f"Webhook setup: {response.json()}")
        except Exception as e:
            logger.error(f"Webhook setup failed: {e}")

    def verify_chat_id(self, incoming_chat_id):
        return str(incoming_chat_id) == str(self.chat_id)

    def get_auth_token(self):
        auth_url = "https://api-seller.uzum.uz/api/seller/v1/account/token"
        payload = {
            "username": self.uzum_username,
            "password": self.uzum_password
        }
        response = requests.post(auth_url, json=payload)
        if response.status_code == 200:
            return response.json().get('access_token')
        raise Exception(f"Auth failed: {response.text}")

    def get_new_orders(self):
        try:
            token = self.get_auth_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            last_check = self.storage.get_last_check_time()
            from_time = int(last_check.timestamp() * 1000)
            
            params = {
                'from': from_time,
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
                    params=params
                )
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                if not data.get('data'):
                    break
                    
                orders.extend(data['data'])
                page += 1
                
            return orders
        except Exception as e:
            logger.error(f"Order fetch error: {e}")
            return []

    def send_telegram_message(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        requests.post(url, json=payload)

    def format_order_message(self, order):
        created_at = datetime.fromtimestamp(order['createdAt']/1000).strftime('%Y-%m-%d %H:%M:%S')
        items_text = "\n".join([
            f"- {item['productName']} × {item['quantity']} ({item['price']} UZS)"
            for item in order['items']
        ])
        
        return f"""
🛍️ <b>New Uzum Order!</b>

📦 <b>Order ID:</b> <code>{order['id']}</code>
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
        @app.route('/webhook', methods=['POST'])
        def webhook_handler():
            update = request.json
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                if not self.verify_chat_id(chat_id):
                    logger.warning(f"Unauthorized access from {chat_id}")
                    return jsonify({"status": "unauthorized"}), 403
                
                if '/start' in update['message'].get('text', ''):
                    self.send_telegram_message("✅ Bot is active and monitoring your Uzum orders!")
            
            return jsonify({"status": "ok"}), 200

        @app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy"}), 200

        # Start order checking in background
        from threading import Thread
        Thread(target=self._check_orders_loop, daemon=True).start()
        
        return app

    def _check_orders_loop(self):
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
                logger.error(f"Order check loop failed: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = UzumOrderBot()
    app = bot.run()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
