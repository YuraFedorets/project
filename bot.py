"""
bot.py — Файл 4: Telegram бот.
Містить конфігурацію, надсилання повідомлень,
сповіщення адмінів та фоновий polling.
"""

import re
import threading
import sqlite3 as _sq
import requests as req_lib

# ── Конфігурація ───────────────────────────────────────────────────────────────
TG_TOKEN  = '8508685213:AAGWKzmjGfcBbW0yS1DbcpfMI4g4NoIvPcE'
TG_GROUP  = -5284724066
TG_ADMINS = {785579199, 713037789}
TG_API    = f'https://api.telegram.org/bot{TG_TOKEN}'

# Зв'язок: tg_message_id → conv_key
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
    """Повідомити адміна про нове повідомлення в чаті підтримки."""
    text = (
        f'💬 <b>Нове повідомлення в підтримці</b>\n'
        f'👤 <b>Від:</b> {sender_name}\n'
        f'🔑 <b>Ключ:</b> <code>{conv_key}</code>\n'
        f'📝 <b>Текст:</b> {message}\n\n'
        f'<i>Щоб відповісти — просто відповідай на це повідомлення в Telegram</i>'
    )
    result = tg_send(TG_GROUP, text)
    msg_id = result.get('result', {}).get('message_id')
    if msg_id:
        TG_MSG_MAP[msg_id] = conv_key
    return msg_id


def _polling_loop():
    """Фоновий polling — слухає відповіді адміна і зберігає їх у БД."""
    import time
    offset = 0
    print('[TG] Polling started')

    while True:
        try:
            r = req_lib.get(f'{TG_API}/getUpdates',
                            params={'timeout': 30, 'offset': offset}, timeout=35)
            updates = r.json().get('result', [])

            for upd in updates:
                offset = upd['update_id'] + 1
                msg = upd.get('message', {})
                if not msg:
                    continue

                text         = msg.get('text', '').strip()
                from_id      = msg.get('from', {}).get('id')
                chat_id      = msg.get('chat', {}).get('id')
                reply_to_msg = msg.get('reply_to_message', {})
                reply_to     = reply_to_msg.get('message_id')

                is_from_admin = from_id in TG_ADMINS
                is_from_group = chat_id == TG_GROUP

                if not text or not reply_to:
                    continue
                if not (is_from_admin or is_from_group):
                    continue

                # Шукаємо conv_key в пам'яті
                conv_key = TG_MSG_MAP.get(reply_to)

                # Якщо не знайшли — витягуємо з тексту оригінального повідомлення
                if not conv_key:
                    orig_text = reply_to_msg.get('text', '')
                    m = re.search(r'Ключ: ([\w_]+)', orig_text)
                    if m:
                        conv_key = m.group(1)

                if not conv_key:
                    continue

                # Зберігаємо відповідь у БД
                try:
                    sender_name = msg.get('from', {}).get('first_name', 'Адміністратор')
                    db2 = _sq.connect('ukd_database.db')
                    db2.row_factory = _sq.Row
                    db2.execute("""
                        INSERT INTO support_messages
                            (sender_type, sender_id, sender_name, message, session_key, is_read)
                        VALUES ('admin', 0, ?, ?, ?, 1)
                    """, (sender_name, text, conv_key))
                    db2.commit()
                    db2.close()
                    tg_send(TG_GROUP,
                            f'✅ <b>{sender_name}</b> відповів у чат <code>{conv_key}</code>',
                            reply_to=msg['message_id'])
                    print(f'[TG] Reply from {sender_name} saved to conv {conv_key}')
                except Exception as e:
                    print(f'[TG] DB error: {e}')
                    tg_send(TG_GROUP, f'❌ Помилка збереження: {e}')

        except Exception as e:
            print(f'[TG] polling error: {e}')
            time.sleep(5)


def start_tg_polling():
    """Запускає polling у фоновому потоці."""
    t = threading.Thread(target=_polling_loop, daemon=True)
    t.start()
    return t
