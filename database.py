"""
database.py — Файл 5 (логіка): Робота з базою даних SQLite.
Фізичний файл БД: ukd_database.db (завантажений оригінал).
Містить: підключення, ініціалізацію таблиць, закриття з'єднання.
"""

import sqlite3
from flask import g

DATABASE = 'ukd_database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER UNIQUE,
            company_name TEXT UNIQUE NOT NULL,
            description  TEXT,
            contact_info TEXT,
            avatar       TEXT DEFAULT 'https://cdn-icons-png.flaticon.com/512/3061/3061341.png',
            position     TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            role       TEXT NOT NULL DEFAULT 'STUDENT',
            company_id INTEGER,
            position   TEXT,
            status     TEXT DEFAULT 'active',
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT UNIQUE,
            email        TEXT UNIQUE,
            password     TEXT DEFAULT '123',
            status       TEXT DEFAULT 'active',
            first_name   TEXT,
            last_name    TEXT,
            patronymic   TEXT,
            course       TEXT,
            specialty    TEXT,
            skills       TEXT,
            links        TEXT,
            contact_info TEXT,
            rating       INTEGER DEFAULT 0,
            avatar       TEXT DEFAULT 'https://cdn-icons-png.flaticon.com/512/354/354637.png'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            status      TEXT DEFAULT 'active',
            admin_level INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            company_id INTEGER,
            user_id    INTEGER,
            message    TEXT,
            status     TEXT DEFAULT 'pending',
            flagged    BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (user_id)    REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_type TEXT NOT NULL,
            sender_id   INTEGER,
            sender_name TEXT,
            message     TEXT NOT NULL,
            reply       TEXT,
            replied_at  TIMESTAMP,
            session_key TEXT,
            is_read     INTEGER DEFAULT 0,
            is_archived INTEGER DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    try:
        cursor.execute("ALTER TABLE support_messages ADD COLUMN is_archived INTEGER DEFAULT 0")
    except Exception:
        pass

    db.commit()

    if not cursor.execute("SELECT * FROM admins WHERE username = 'admin'").fetchone():
        cursor.execute(
            "INSERT INTO admins (username, email, password, admin_level) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@ukd.edu.ua', '123', 10)
        )
        db.commit()
