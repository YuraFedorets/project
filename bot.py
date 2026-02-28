"""
bot.py — Файл 4: Telegram бот.

ВИПРАВЛЕННЯ:
  1. Відповідь з групи приймається від будь-якого учасника (не тільки TG_ADMINS)
  2. is_read встановлюється в 0 щоб /support/check_new коректно доставив відповідь юзеру
  3. conv_key відновлюється з тексту повідомлення навіть після перезапуску сервера
"""

import re
import time
import threading
import sqlite3 as _sq
import requests as req_lib

# ── Конфігурація ───────────────────────────────────────────────────────────────
TG_TOKEN  = '8508685213:AAGWKzmjGfcBbW0yS1DbcpfMI4g4NoIvPcE'
TG_GROUP  = -5284724066
TG_ADMINS = {785579199, 713037789}
TG_API    = f'https://api.telegram.org/bot{TG_TOKEN}'

# Зв'язок: tg_message_id → conv_key (в пам'яті процесу)
TG_MSG_MAP: dict = {}


def tg_send(chat_id: int, text: str, reply_to: int = None) -> dict:
    """Надіслати повідомлення через Telegram."""
    try:
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        if reply_to:
            payload['reply_to_message_id'] = reply_to
        r = req_lib.post(f'{TG_API}/sendMessage', json=payload, timeout=5)
        return r.json()
    except Exception as e:
        print(f'[TG] send error: {e}')
        return {}


def tg_notify_admin(sender_name: str, conv_key: str, message: str) -> int:
    """Відправити нове повідомлення юзера в Telegram групу адміна."""
    text = (
        f'💬 <b>Нове повідомлення в підтримці</b>\n'
        f'👤 <b>Від:</b> {sender_name}\n'
        f'🔑 <b>Ключ:</b> <code>{conv_key}</code>\n'
        f'📝 <b>Текст:</b> {message}\n\n'
        f'<i>Щоб відповісти — зроби Reply саме на це повідомлення</i>'
    )
    result = tg_send(TG_GROUP, text)
    msg_id = result.get('result', {}).get('message_id')
    if msg_id:
        TG_MSG_MAP[msg_id] = conv_key
        print(f'[TG] Збережено: msg_id={msg_id} → conv_key={conv_key}')
    return msg_id


def _polling_loop():
    """
    Фоновий polling — приймає reply адміна з Telegram і зберігає в БД.

    ПРАВИЛА ПРИЙОМУ:
      - Повідомлення ОБОВ'ЯЗКОВО має бути reply (reply_to_message існує)
      - Повідомлення з групи TG_GROUP — приймаємо від БУДЬ-ЯКОГО учасника групи
      - Або особисте повідомлення від когось із TG_ADMINS (DM боту)
      - Ігноруємо повідомлення самого бота (is_bot=True)

    ПОШУК conv_key:
      1. Спочатку шукаємо в TG_MSG_MAP (швидко, в пам'яті)
      2. Якщо сервер перезапускався — витягуємо з тексту оригінального повідомлення
         через regex: "Ключ: <conv_key>"
    """
    offset = 0
    print('[TG] Polling started')

    while True:
        try:
            r = req_lib.get(
                f'{TG_API}/getUpdates',
                params={'timeout': 30, 'offset': offset},
                timeout=35
            )
            updates = r.json().get('result', [])

            for upd in updates:
                offset = upd['update_id'] + 1
                msg = upd.get('message', {})
                if not msg:
                    continue

                text          = msg.get('text', '').strip()
                from_id       = msg.get('from', {}).get('id')
                from_is_bot   = msg.get('from', {}).get('is_bot', False)
                chat_id       = msg.get('chat', {}).get('id')
                reply_to_msg  = msg.get('reply_to_message', {})
                reply_to      = reply_to_msg.get('message_id')

                # Пропускаємо якщо: немає тексту, не reply, або пише сам бот
                if not text or not reply_to or from_is_bot:
                    continue

                # Приймаємо тільки reply з групи або DM від адміна
                is_from_group = (chat_id == TG_GROUP)
                is_admin_dm   = (from_id in TG_ADMINS)
                if not (is_from_group or is_admin_dm):
                    continue

                # Знаходимо conv_key
                conv_key = TG_MSG_MAP.get(reply_to)
                if not conv_key:
                    # Відновлення після перезапуску — шукаємо в тексті
                    orig_text = reply_to_msg.get('text', '')
                    match = re.search(r'Ключ:\s*([\w_]+)', orig_text)
                    if match:
                        conv_key = match.group(1)
                        print(f'[TG] conv_key відновлено з тексту: {conv_key}')

                if not conv_key:
                    print(f'[TG] reply_to={reply_to} — conv_key не знайдено, ігноруємо')
                    continue

                # Зберігаємо відповідь у БД
                # ВАЖЛИВО: is_read=0 — щоб /support/check_new доставив відповідь юзеру
                try:
                    sender_name = msg.get('from', {}).get('first_name', 'Адміністратор')
                    db2 = _sq.connect('ukd_database.db')
                    db2.row_factory = _sq.Row
                    db2.execute("""
                        INSERT INTO support_messages
                            (sender_type, sender_id, sender_name, message, session_key, is_read)
                        VALUES ('admin', 0, ?, ?, ?, 0)
                    """, (sender_name, text, conv_key))
                    db2.commit()
                    db2.close()

                    tg_send(
                        TG_GROUP,
                        f'✅ <b>{sender_name}</b> відповів у чат <code>{conv_key}</code>',
                        reply_to=msg['message_id']
                    )
                    print(f'[TG] Відповідь збережена: {sender_name} → {conv_key}')

                except Exception as e:
                    print(f'[TG] DB error: {e}')
                    tg_send(TG_GROUP, f'❌ Помилка збереження: {e}')

        except Exception as e:
            print(f'[TG] polling error: {e}')
            time.sleep(5)


def start_tg_polling():
    """Запускає polling у фоновому daemon-потоці."""
    t = threading.Thread(target=_polling_loop, daemon=True)
    t.start()
    return t
