"""
database.py — Робота з базою даних через SQLAlchemy + Flask-Migrate.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_extensions(app):
    """Ініціалізація SQLAlchemy та Flask-Migrate."""
    db.init_app(app)
    # Імпортуємо моделі тут, щоб Flask-Migrate їх бачив
    from models.user import Admin, User, Student, Company, Invitation, SupportMessage
    migrate.init_app(app, db)


def close_connection(exception):
    """Закриття сесії після кожного запиту."""
    db.session.remove()


def seed_default_admin():
    from models.user import Admin  # локальний імпорт щоб уникнути циклічних залежностей

    username = os.getenv('ADMIN_USERNAME')
    email    = os.getenv('ADMIN_EMAIL')
    password = os.getenv('ADMIN_PASSWORD')
    level    = os.getenv('ADMIN_LEVEL')

    if not all([username, email, password]):
        print("Помилка: Дані адміна не знайдені в .env файлі!")
        return

    if not Admin.query.filter_by(username=username).first():
        db.session.add(Admin(
            username    = username,
            email       = email,
            password    = password,
            admin_level = int(level) if level else 1
        ))
        db.session.commit()
        print(f"Адмін {username} успішно створений з даними з .env")