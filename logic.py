"""
logic.py — Файл 3: Вся логіка проекту.
Містить всі Flask маршрути (routes): авторизацію, профілі,
запрошення, підтримку, адмін-панель та API.
"""

import sqlite3
import uuid
import threading
from flask import request, session, redirect, flash, jsonify, render_template_string, g
from database import get_db


def register_routes(app, HTML_TEMPLATE):
    """Реєструє всі маршрути в переданий Flask-додаток."""

    # ── Допоміжна функція рендеру ──────────────────────────────────────────────
    def render(active_tab='home', **kwargs):
        db = get_db()

        # Студенти (для рейтингу)
        students = kwargs.get('students', [])
        current_filters = kwargs.get('current_filters', {'search': '', 'course': '', 'specialty': '', 'sort': 'desc'})
        unique_courses = kwargs.get('unique_courses', [])
        unique_specialties = kwargs.get('unique_specialties', [])

        # Адмін-дані
        all_students = kwargs.get('all_students', [])

        # Компанії (завжди для модалки)
        all_companies = kwargs.get('all_companies', [])
        if not all_companies:
            for comp in db.execute("SELECT * FROM companies ORDER BY company_name").fetchall():
                c = dict(comp)
                c["employees"] = []
                all_companies.append(c)

        # Профіль
        user_info = kwargs.get('user_info', {})
        profile_data = kwargs.get('profile_data', {})

        # Запрошення
        invitations = kwargs.get('invitations', [])
        pending_count = kwargs.get('pending_count', 0)

        # Підтримка
        unread_support_count = 0
        support_conversations = kwargs.get('support_conversations', [])
        active_conv_key = kwargs.get('active_conv_key', None)
        active_conv_messages = kwargs.get('active_conv_messages', [])
        active_conv_sender = kwargs.get('active_conv_sender', None)
        show_archived = kwargs.get('show_archived', False)

        if session.get('role') == 'ADMIN':
            res = db.execute("SELECT COUNT(*) as c FROM support_messages WHERE is_read=0 AND sender_type != 'admin' AND is_archived=0").fetchone()
            unread_support_count = res['c'] if res else 0

        return render_template_string(
            HTML_TEMPLATE,
            active_tab=active_tab,
            students=students,
            all_students=all_students,
            all_companies=all_companies,
            user_info=user_info,
            profile_data=profile_data,
            invitations=invitations,
            pending_count=pending_count,
            current_filters=current_filters,
            unique_courses=unique_courses,
            unique_specialties=unique_specialties,
            unread_support_count=unread_support_count,
            support_conversations=support_conversations,
            active_conv_key=active_conv_key,
            active_conv_messages=active_conv_messages,
            active_conv_sender=active_conv_sender,
            show_archived=show_archived,
            all_users=[]
        )

    # ══════════════════════════════════════════════════════════════════════
    # ГОЛОВНА СТОРІНКА
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/')
    def index():
        from database import init_db
        init_db()

        if 'user_id' not in session:
            return render_template_string(HTML_TEMPLATE, active_tab='landing',
                                          students=[], all_students=[], all_companies=[],
                                          user_info={}, profile_data={}, invitations=[],
                                          pending_count=0, current_filters={},
                                          unique_courses=[], unique_specialties=[],
                                          unread_support_count=0, support_conversations=[],
                                          active_conv_key=None, active_conv_messages=[],
                                          active_conv_sender=None, show_archived=False, all_users=[])

        active_tab = request.args.get('tab', 'home')
        db = get_db()

        # ── Фільтри рейтингу ──
        search_query    = request.args.get('search', '').strip()
        course_filter   = request.args.get('course', '').strip()
        specialty_filter = request.args.get('specialty', '').strip()
        sort_order      = request.args.get('sort', 'desc')
        current_filters = {'search': search_query, 'course': course_filter,
                           'specialty': specialty_filter, 'sort': sort_order}

        unique_courses, unique_specialties = [], []
        if active_tab == 'ranking':
            unique_courses     = [r['course'] for r in db.execute("SELECT DISTINCT course FROM students WHERE course IS NOT NULL AND course != '' ORDER BY course").fetchall()]
            unique_specialties = [r['specialty'] for r in db.execute("SELECT DISTINCT specialty FROM students WHERE specialty IS NOT NULL AND specialty != '' ORDER BY specialty").fetchall()]

        # ── Список студентів ──
        students = []
        if active_tab == 'ranking':
            q = "SELECT s.* FROM students s WHERE s.status != 'blocked'"
            params = []
            if search_query:
                q += " AND (s.first_name LIKE ? OR s.last_name LIKE ? OR s.skills LIKE ? OR s.specialty LIKE ?)"
                params.extend([f'%{search_query}%'] * 4)
            if course_filter:
                q += " AND s.course = ?"
                params.append(course_filter)
            if specialty_filter:
                q += " AND s.specialty = ?"
                params.append(specialty_filter)
            q += " ORDER BY s.rating " + ("ASC" if sort_order == 'asc' else "DESC")
            students = [dict(r) for r in db.execute(q, params).fetchall()]

        # ── Адмін: студенти та компанії ──
        all_students, all_companies = [], []
        if active_tab in ('users', 'companies') and session.get('role') == 'ADMIN':
            all_students = [dict(r) for r in db.execute("SELECT * FROM students ORDER BY last_name").fetchall()]
            for comp in db.execute("SELECT * FROM companies ORDER BY company_name").fetchall():
                c = dict(comp)
                c["employees"] = [dict(e) for e in db.execute("SELECT * FROM users WHERE company_id=? ORDER BY role,username", (c["id"],)).fetchall()]
                all_companies.append(c)
        if not all_companies:
            for comp in db.execute("SELECT * FROM companies ORDER BY company_name").fetchall():
                c = dict(comp)
                c["employees"] = []
                all_companies.append(c)

        # ── Профіль ──
        user_info, profile_data = {}, {}
        if 'user_id' in session:
            target_id = session.get('edit_target_id', session['user_id'])
            role = session.get('role')

            if role == 'ADMIN':
                if session.get('edit_target_id'):
                    row = db.execute("SELECT * FROM students WHERE id = ?", (target_id,)).fetchone()
                    if row:
                        user_info = dict(row)
                        user_info['role'] = 'STUDENT'
                        profile_data = user_info
                    else:
                        row = db.execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()
                        if row:
                            user_info = dict(row)
                            comp = db.execute("SELECT * FROM companies WHERE id = ?", (user_info.get('company_id'),)).fetchone()
                            profile_data = dict(comp) if comp else {}
                        else:
                            row = db.execute("SELECT * FROM admins WHERE id = ?", (session['user_id'],)).fetchone()
                            user_info = dict(row) if row else {}
                            user_info['role'] = 'ADMIN'
                            profile_data = user_info
                else:
                    row = db.execute("SELECT * FROM admins WHERE id = ?", (target_id,)).fetchone()
                    user_info = dict(row) if row else {}
                    user_info['role'] = 'ADMIN'
                    profile_data = user_info
            elif role == 'STUDENT':
                row = db.execute("SELECT * FROM students WHERE id = ?", (target_id,)).fetchone()
                user_info = dict(row) if row else {}
                user_info['role'] = 'STUDENT'
                profile_data = user_info
            else:
                row = db.execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()
                user_info = dict(row) if row else {}
                comp_id = user_info.get('company_id')
                if comp_id:
                    comp = db.execute("SELECT * FROM companies WHERE id = ?", (comp_id,)).fetchone()
                    profile_data = dict(comp) if comp else {}

        # ── Запрошення ──
        invitations, pending_count = [], 0
        if session.get('role') == 'STUDENT':
            res = db.execute("SELECT COUNT(*) as c FROM invitations i WHERE i.student_id = ? AND i.status='pending'", (session['user_id'],)).fetchone()
            pending_count = res['c']

        if active_tab == 'invitations':
            role = session.get('role')
            if role == 'ADMIN':
                invitations = [dict(r) for r in db.execute("""
                    SELECT i.*, s.first_name, s.last_name, c.company_name, c.avatar as company_avatar
                    FROM invitations i
                    LEFT JOIN students s ON i.student_id = s.id
                    LEFT JOIN companies c ON i.company_id = c.id
                    ORDER BY i.created_at DESC
                """).fetchall()]
            elif role in ('COMPANY_ADMIN', 'EMPLOYEE'):
                comp_id = session.get('company_id')
                if comp_id:
                    invitations = [dict(r) for r in db.execute("""
                        SELECT i.*, s.first_name, s.last_name, c.company_name, c.avatar as company_avatar
                        FROM invitations i
                        JOIN students s ON i.student_id = s.id
                        LEFT JOIN companies c ON i.company_id = c.id
                        WHERE i.company_id = ?
                        ORDER BY i.created_at DESC
                    """, (comp_id,)).fetchall()]
            elif role == 'STUDENT':
                invitations = [dict(r) for r in db.execute("""
                    SELECT i.*, c.company_name, c.avatar as company_avatar
                    FROM invitations i
                    LEFT JOIN companies c ON i.company_id = c.id
                    WHERE i.student_id = ?
                    ORDER BY i.created_at DESC
                """, (session['user_id'],)).fetchall()]

        # ── Підтримка (Admin) ──
        support_conversations, active_conv_key, active_conv_messages, active_conv_sender = [], None, [], None
        show_archived = bool(request.args.get('show_archived'))

        if session.get('role') == 'ADMIN' and active_tab == 'support':
            archived_filter = "AND sm.is_archived=1" if show_archived else "AND sm.is_archived=0"
            convs = db.execute(f"""
                SELECT session_key, sender_name,
                       MAX(created_at) as last_time,
                       (SELECT message FROM support_messages sm2 WHERE sm2.session_key = sm.session_key ORDER BY sm2.created_at DESC LIMIT 1) as last_message,
                       SUM(CASE WHEN is_read=0 AND sender_type != 'admin' THEN 1 ELSE 0 END) as unread_count
                FROM support_messages sm
                WHERE sender_type != 'admin' {archived_filter}
                GROUP BY session_key
                ORDER BY last_time DESC
            """).fetchall()
            support_conversations = [dict(c) for c in convs]

            active_conv_key = request.args.get('conv_key') or (support_conversations[0]['session_key'] if support_conversations else None)
            if active_conv_key:
                active_conv_messages = [dict(m) for m in db.execute(
                    "SELECT * FROM support_messages WHERE session_key=? ORDER BY created_at ASC", (active_conv_key,)).fetchall()]
                db.execute("UPDATE support_messages SET is_read=1 WHERE session_key=? AND sender_type!='admin'", (active_conv_key,))
                db.commit()
                sender_row = db.execute("SELECT sender_name FROM support_messages WHERE session_key=? AND sender_type!='admin' LIMIT 1", (active_conv_key,)).fetchone()
                active_conv_sender = sender_row['sender_name'] if sender_row else 'Гість'

        return render(active_tab,
                      students=students, current_filters=current_filters,
                      unique_courses=unique_courses, unique_specialties=unique_specialties,
                      all_students=all_students, all_companies=all_companies,
                      user_info=user_info, profile_data=profile_data,
                      invitations=invitations, pending_count=pending_count,
                      support_conversations=support_conversations,
                      active_conv_key=active_conv_key,
                      active_conv_messages=active_conv_messages,
                      active_conv_sender=active_conv_sender,
                      show_archived=show_archived)

    # ══════════════════════════════════════════════════════════════════════
    # АВТОРИЗАЦІЯ
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/login', methods=['POST'])
    def login():
        login_input = (request.form.get('username') or '').strip()
        password    = request.form.get('password')
        db = get_db()

        # Адміни
        admin = db.execute("SELECT * FROM admins WHERE (username = ? OR email = ?) AND password = ?",
                           (login_input, login_input, password)).fetchone()
        if admin:
            if dict(admin).get('status') == 'blocked':
                flash("Ваш акаунт заблоковано.")
                return redirect('/')
            session.update({'user_id': admin['id'], 'role': 'ADMIN',
                            'username': admin['username'], 'company_id': None})
            session.pop('edit_target_id', None)
            return redirect('/')

        # Студенти
        student = db.execute("SELECT * FROM students WHERE (username = ? OR email = ?) AND password = ?",
                             (login_input, login_input, password)).fetchone()
        if student:
            if dict(student).get('status') == 'blocked':
                flash("Ваш акаунт заблоковано.")
                return redirect('/')
            session.update({'user_id': student['id'], 'role': 'STUDENT',
                            'username': student['username'], 'company_id': None})
            session.pop('edit_target_id', None)
            return redirect('/')

        # Працівники компаній
        user = db.execute("SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
                          (login_input, login_input, password)).fetchone()
        if user:
            if dict(user).get('status') == 'blocked':
                flash("Ваш акаунт заблоковано.")
                return redirect('/')
            session.update({'user_id': user['id'], 'role': user['role'],
                            'username': user['username'], 'company_id': user['company_id']})
            session.pop('edit_target_id', None)
            return redirect('/')

        flash("Невірні дані для входу")
        return redirect('/')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')

    # ══════════════════════════════════════════════════════════════════════
    # ПРОФІЛЬ
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/update_profile', methods=['POST'])
    def update_profile():
        if 'user_id' not in session:
            return redirect('/')
        target_id = session.get('edit_target_id', session['user_id'])
        if target_id != session['user_id'] and session['role'] != 'ADMIN':
            return "Access Denied", 403

        db = get_db()
        role = session.get('role')

        # Визначаємо роль цільового користувача
        if role == 'ADMIN' and session.get('edit_target_id'):
            if db.execute("SELECT id FROM students WHERE id = ?", (target_id,)).fetchone():
                target_role = 'STUDENT'
            else:
                row = db.execute("SELECT role FROM users WHERE id = ?", (target_id,)).fetchone()
                target_role = row['role'] if row else 'ADMIN'
        elif role == 'STUDENT':
            target_role = 'STUDENT'
        elif role == 'ADMIN':
            target_role = 'ADMIN'
        else:
            row = db.execute("SELECT role FROM users WHERE id = ?", (target_id,)).fetchone()
            target_role = row['role'] if row else 'EMPLOYEE'

        if target_role == 'STUDENT':
            if role == 'ADMIN':
                rating_val = request.form.get('rating')
                if rating_val is not None:
                    db.execute("UPDATE students SET rating=? WHERE id=?", (int(rating_val), target_id))
            new_email = request.form.get('email')
            db.execute("""
                UPDATE students SET first_name=?, last_name=?, patronymic=?, course=?,
                specialty=?, skills=?, links=?, contact_info=?, avatar=?, email=?, username=?
                WHERE id=?
            """, (request.form.get('first_name'), request.form.get('last_name'),
                  request.form.get('patronymic'), request.form.get('course'),
                  request.form.get('specialty'), request.form.get('skills'),
                  request.form.get('links'), request.form.get('contact_info'),
                  request.form.get('avatar'), new_email, new_email, target_id))

        elif target_role in ('COMPANY', 'COMPANY_ADMIN', 'EMPLOYEE'):
            new_email = request.form.get('email')
            if new_email and role == 'ADMIN':
                db.execute("UPDATE users SET email=?, username=? WHERE id=?", (new_email, new_email, target_id))
            row = db.execute('SELECT company_id FROM users WHERE id=?', (target_id,)).fetchone()
            if row and row['company_id']:
                db.execute("""
                    UPDATE companies SET company_name=?, description=?, avatar=?, position=?, contact_info=?
                    WHERE id=?
                """, (request.form.get('company_name'), request.form.get('description'),
                      request.form.get('avatar'), request.form.get('position'),
                      request.form.get('contact_info'), row['company_id']))

        db.commit()
        flash("Профіль успішно оновлено!")
        return redirect('/?tab=profile')

    @app.route('/admin/select_user', methods=['POST'])
    def admin_select_user():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        try:
            session['edit_target_id'] = int(request.form.get('target_user_id'))
            flash(f"Режим редагування користувача ID: {session['edit_target_id']}")
        except Exception:
            flash("Невірний ID")
        return redirect('/?tab=profile')

    # ══════════════════════════════════════════════════════════════════════
    # ЗАПРОШЕННЯ
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/send_invite', methods=['POST'])
    def send_invite():
        if 'user_id' not in session:
            return redirect('/')
        db = get_db()
        student_id = request.form.get('student_id')
        message    = request.form.get('message')
        row = db.execute("SELECT company_id FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        comp_id = row['company_id'] if row else None
        db.execute("INSERT INTO invitations (student_id, company_id, user_id, message, status) VALUES (?, ?, ?, ?, 'pending')",
                   (student_id, comp_id, session['user_id'], message))
        db.commit()
        flash("Запрошення надіслано!")
        return redirect('/?tab=ranking')

    @app.route('/respond_invite', methods=['POST'])
    def respond_invite():
        if session.get('role') != 'STUDENT':
            return redirect('/')
        invite_id  = request.form.get('invite_id')
        action     = request.form.get('action')
        new_status = 'accepted' if action == 'accept' else 'rejected'
        db = get_db()
        db.execute("UPDATE invitations SET status = ? WHERE id = ?", (new_status, invite_id))
        db.commit()
        flash("Ви прийняли пропозицію!" if new_status == 'accepted' else "Ви відхилили пропозицію.")
        return redirect('/?tab=invitations')

    @app.route('/delete_invite', methods=['POST'])
    def delete_invite():
        if session.get('role') not in ('ADMIN', 'COMPANY_ADMIN', 'EMPLOYEE'):
            return redirect('/')
        invite_id = request.form.get('invite_id')
        db = get_db()
        if session.get('role') != 'ADMIN':
            comp_id = session.get('company_id')
            inv = db.execute("SELECT company_id FROM invitations WHERE id=?", (invite_id,)).fetchone()
            if not inv or inv['company_id'] != comp_id:
                flash("Доступ заборонено.")
                return redirect('/?tab=invitations')
        db.execute("DELETE FROM invitations WHERE id = ?", (invite_id,))
        db.commit()
        flash("Заявку успішно видалено.")
        return redirect('/?tab=invitations')

    # ══════════════════════════════════════════════════════════════════════
    # АДМІН-ПАНЕЛЬ
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/admin/toggle_block', methods=['POST'])
    def admin_toggle_block():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        user_id   = request.form.get('user_id')
        user_type = request.form.get('user_type', 'employee')
        db = get_db()
        if user_type == 'student':
            db.execute("UPDATE students SET status = CASE WHEN status='blocked' THEN 'active' ELSE 'blocked' END WHERE id=?", (user_id,))
            tab = 'users'
        else:
            db.execute("UPDATE users SET status = CASE WHEN status='blocked' THEN 'active' ELSE 'blocked' END WHERE id=?", (user_id,))
            tab = 'companies'
        db.commit()
        flash("Статус змінено.")
        return redirect(f'/?tab={tab}')

    @app.route('/admin/delete_user', methods=['POST'])
    def admin_delete_user():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        user_id   = request.form.get('user_id')
        user_type = request.form.get('user_type', 'employee')
        db = get_db()
        if user_type == 'student':
            db.execute("DELETE FROM invitations WHERE student_id=?", (user_id,))
            db.execute("DELETE FROM students WHERE id=?", (user_id,))
            flash("Студента видалено.")
            return redirect('/?tab=users')
        else:
            db.execute("DELETE FROM invitations WHERE user_id=?", (user_id,))
            db.execute("DELETE FROM users WHERE id=?", (user_id,))
            flash("Працівника видалено.")
            return redirect('/?tab=companies')

    @app.route('/admin/create_company', methods=['POST'])
    def admin_create_company():
        if session.get('role') != 'ADMIN':
            flash("Доступ заборонено.")
            return redirect('/')
        company_name = request.form.get('company_name')
        email        = request.form.get('email')
        username     = request.form.get('username') or email
        password     = request.form.get('password')
        db = get_db()
        try:
            db.execute("INSERT INTO companies (company_name) VALUES (?)", (company_name,))
            company_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute("INSERT INTO users (username, email, password, role, company_id, position, status) VALUES (?, ?, ?, 'COMPANY_ADMIN', ?, 'Директор', 'active')",
                       (email, email, password, company_id))
            new_user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute("UPDATE companies SET user_id=? WHERE id=?", (new_user_id, company_id))
            db.commit()
            flash(f"Компанію '{company_name}' створено! Логін директора: {email}")
        except Exception as e:
            flash(f"Помилка: {e}")
        return redirect('/?tab=users')

    @app.route('/admin/add_employee', methods=['POST'])
    def admin_add_employee():
        if session.get('role') != 'ADMIN':
            flash("Доступ заборонено.")
            return redirect('/')
        email      = request.form.get('email', '').strip()
        position   = request.form.get('position', '').strip()
        password   = request.form.get('password', '').strip()
        company_id = request.form.get('company_id')
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, email, password, role, company_id, position, status) VALUES (?, ?, ?, 'EMPLOYEE', ?, ?, 'active')",
                       (email, email, password, company_id, position))
            db.commit()
            flash(f"Працівника '{email}' додано до компанії!")
        except Exception as e:
            flash(f"Помилка: {e}")
        return redirect('/?tab=companies')

    @app.route('/company/add_employee', methods=['POST'])
    def company_add_employee():
        if session.get('role') != 'COMPANY_ADMIN':
            flash("Доступ заборонено.")
            return redirect('/')
        email      = request.form.get('email', '').strip()
        position   = request.form.get('position', '').strip()
        password   = request.form.get('password', '').strip()
        company_id = session.get('company_id')
        if not company_id:
            flash("Не вдалося визначити вашу компанію.")
            return redirect('/')
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, email, password, role, company_id, position, status) VALUES (?, ?, ?, 'EMPLOYEE', ?, ?, 'active')",
                       (email, email, password, company_id, position))
            db.commit()
            flash(f"Робітника '{email}' успішно додано!")
        except Exception as e:
            flash(f"Помилка: {e}")
        return redirect('/?tab=invitations')

    # ══════════════════════════════════════════════════════════════════════
    # ЧАТ ПІДТРИМКИ
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/admin/support_archive', methods=['POST'])
    def admin_support_archive():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        conv_key = request.form.get('conv_key')
        action   = request.form.get('action', 'archive')
        db = get_db()
        if action == 'archive':
            db.execute("UPDATE support_messages SET is_archived=1 WHERE session_key=?", (conv_key,))
            flash("Діалог переміщено в архів.")
        elif action == 'unarchive':
            db.execute("UPDATE support_messages SET is_archived=0 WHERE session_key=?", (conv_key,))
            flash("Діалог відновлено.")
        elif action == 'delete':
            db.execute("DELETE FROM support_messages WHERE session_key=?", (conv_key,))
            flash("Діалог видалено назавжди.")
        db.commit()
        suffix = '&show_archived=1' if action == 'unarchive' else ''
        return redirect(f'/?tab=support{suffix}')

    @app.route('/admin/support_reply', methods=['POST'])
    def admin_support_reply():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        conv_key = request.form.get('conv_key')
        reply    = request.form.get('reply')
        db = get_db()
        db.execute("UPDATE support_messages SET is_read=1 WHERE session_key=?", (conv_key,))
        db.execute("""
            INSERT INTO support_messages (sender_type, sender_id, sender_name, message, session_key, is_read)
            VALUES ('admin', ?, 'Адміністратор', ?, ?, 1)
        """, (session['user_id'], reply, conv_key))
        db.commit()

        # Сповіщення в Telegram
        from bot import tg_send, TG_GROUP
        threading.Thread(
            target=lambda: tg_send(TG_GROUP, f'✅ Відповідь надіслана через сайт у чат <code>{conv_key}</code>:\n{reply}'),
            daemon=True
        ).start()

        flash("Відповідь надіслано!")
        return redirect(f'/?tab=support&conv_key={conv_key}')

    @app.route('/support/send', methods=['POST'])
    def support_send():
        db = get_db()
        message = request.form.get('message', '').strip()
        if not message:
            return jsonify({'ok': False})

        if 'user_id' in session:
            sender_type = session.get('role', 'user').lower()
            sender_id   = session['user_id']
            sender_name = session.get('username', 'User')
            conv_key    = f"user_{session['user_id']}"
        else:
            sender_type = 'guest'
            sender_id   = None
            sender_name = request.form.get('sender_name', 'Гість')
            if 'support_key' not in session:
                session['support_key'] = str(uuid.uuid4())[:8]
            conv_key = f"guest_{session['support_key']}"

        db.execute("""
            INSERT INTO support_messages (sender_type, sender_id, sender_name, message, session_key, is_read)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (sender_type, sender_id, sender_name, message, conv_key))
        db.commit()

        from bot import tg_notify_admin
        threading.Thread(target=lambda: tg_notify_admin(sender_name, conv_key, message), daemon=True).start()

        return jsonify({'ok': True})

    @app.route('/support/history')
    def support_history():
        db = get_db()
        if 'user_id' in session:
            conv_key = f"user_{session['user_id']}"
        elif 'support_key' in session:
            conv_key = f"guest_{session['support_key']}"
        else:
            return jsonify([])
        msgs = db.execute("""
            SELECT id, sender_type, sender_name, message, created_at
            FROM support_messages WHERE session_key=? ORDER BY created_at ASC
        """, (conv_key,)).fetchall()
        return jsonify([dict(m) for m in msgs])

    @app.route('/support/check_new')
    def support_check_new():
        db = get_db()
        last_id = request.args.get('last_id', 0, type=int)
        if 'user_id' in session:
            conv_key = f"user_{session['user_id']}"
        elif 'support_key' in session:
            conv_key = f"guest_{session['support_key']}"
        else:
            return jsonify([])
        msgs = db.execute("""
            SELECT id, sender_type, sender_name, message, created_at
            FROM support_messages
            WHERE session_key=? AND id>? AND sender_type='admin'
            ORDER BY created_at ASC
        """, (conv_key, last_id)).fetchall()
        return jsonify([dict(m) for m in msgs])

    # ══════════════════════════════════════════════════════════════════════
    # API
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/api/student/<int:user_id>')
    def get_student_api(user_id):
        db = get_db()
        std = db.execute("SELECT * FROM students WHERE id = ?", (user_id,)).fetchone()
        if std:
            return jsonify(dict(std))
        return jsonify({"error": "Student not found"}), 404
