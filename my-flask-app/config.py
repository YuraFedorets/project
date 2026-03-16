"""
config.py — Конфігурація проекту УКД Talent.
"""

import os

# ── Flask ──────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'ukd_recruitment_secret_key_v6')
DEBUG      = os.environ.get('DEBUG', 'true').lower() == 'true'
PORT       = int(os.environ.get('PORT', 5000))

# ── База даних ─────────────────────────────────────────────────────────────────
DATABASE = os.environ.get('DATABASE', 'ukd_database.db')

# ── Telegram бот ──────────────────────────────────────────────────────────────
TG_TOKEN  = os.environ.get('TG_TOKEN',  '8508685213:AAGWKzmjGfcBbW0yS1DbcpfMI4g4NoIvPcE')
TG_GROUP  = int(os.environ.get('TG_GROUP', '-5284724066'))
TG_ADMINS = {785579199, 713037789}
