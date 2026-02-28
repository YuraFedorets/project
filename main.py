"""
main.py — Файл 1: Імпорти бібліотек та точка запуску проекту.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Запуск: python main.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ── Стандартні бібліотеки ──────────────────────────────────────────────────────
import os
import sqlite3
import threading
import re
import uuid
from datetime import datetime

# ── Сторонні бібліотеки ────────────────────────────────────────────────────────
import requests
from flask import (
    Flask, render_template_string, request,
    session, redirect, g, flash, jsonify
)

# ── Модулі проекту ─────────────────────────────────────────────────────────────
from database import init_db, get_db, close_connection
from templates import HTML_TEMPLATE
from bot import start_tg_polling
import logic

# ══════════════════════════════════════════════════════════════════════════════
# ІНІЦІАЛІЗАЦІЯ FLASK
# ══════════════════════════════════════════════════════════════════════════════
app = Flask(__name__)
app.secret_key = 'ukd_recruitment_secret_key_v6'

# Реєстрація teardown для автоматичного закриття БД
app.teardown_appcontext(close_connection)

# Реєстрація всіх маршрутів з logic.py
logic.register_routes(app, HTML_TEMPLATE)

# ══════════════════════════════════════════════════════════════════════════════
# СТАРТ
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # Ініціалізація бази даних
    with app.app_context():
        init_db()

    # Запуск Telegram polling у фоновому потоці
    start_tg_polling()

    # Запуск Flask сервера
    app.run(debug=True, port=5000)
