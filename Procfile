web: gunicorn main:app
worker: python -c "from main import UzumOrderBot; UzumOrderBot()._check_orders_loop()"
