"""
app.py — Точка запуску проекту УКД Talent.

Запуск: python app.py
"""

from flask import Flask
from config import SECRET_KEY, DEBUG, PORT
from database import init_db, close_connection
from routes import register_routes
from bot import start_tg_polling

# ── Ініціалізація Flask ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Автоматичне закриття БД після кожного запиту
app.teardown_appcontext(close_connection)

# Реєстрація всіх маршрутів
register_routes(app)

# ── Запуск ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        init_db()

    start_tg_polling()
    app.run(debug=DEBUG, port=PORT)
