"""
app.py — Точка запуску проекту УКД Talent.

Запуск:
    python app.py

Міграції:
    flask db init       # один раз — створює папку migrations/
    flask db migrate -m "initial"
    flask db upgrade
"""

from flask import Flask
from config import SECRET_KEY, DEBUG, PORT, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from database import db, init_extensions, close_connection, seed_default_admin
from routes import register_routes
from bot import start_tg_polling

# ── Ініціалізація Flask ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI']        = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Ініціалізація SQLAlchemy + Flask-Migrate
init_extensions(app)

# Автоматичне закриття сесії БД після кожного запиту
app.teardown_appcontext(close_connection)

# Реєстрація всіх маршрутів
register_routes(app)

# ── Запуск ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()       # створює таблиці якщо їх нема (існуючі не чіпає)
        seed_default_admin()

    start_tg_polling()
    app.run(debug=DEBUG, port=PORT)
