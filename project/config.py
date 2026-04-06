"""
config.py — Конфігурація проекту УКД Talent.
Усі секрети зчитуються з .env файлу.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Flask ──────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG      = os.environ.get('DEBUG', 'true').lower() == 'true'
PORT       = int(os.environ.get('PORT', 5000))

# ── База даних ─────────────────────────────────────────────────────────────────
BASE_DIR                        = os.path.dirname(os.path.abspath(__file__))
DATABASE                        = os.path.join(BASE_DIR, 'ukd_database.db')
SQLALCHEMY_DATABASE_URI         = f'sqlite:///{DATABASE}'
SQLALCHEMY_TRACK_MODIFICATIONS  = False

# ── Telegram бот ──────────────────────────────────────────────────────────────
TG_TOKEN  = os.environ.get('TG_TOKEN')
TG_GROUP  = int(os.environ.get('TG_GROUP', '0'))
TG_ADMINS = set(
    int(x) for x in os.environ.get('TG_ADMINS', '785579199,713037789').split(',') if x.strip()
)
