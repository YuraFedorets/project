"""
routes.py — Всі Flask маршрути проекту УКД Talent.
Використовує Repository Pattern — вся логіка БД в repository/user_repository.py

Структура:
  ├── ЗАГАЛЬНЕ          — допоміжні функції, головна сторінка, авторизація
  ├── ADMIN             — панель адміністратора (користувачі, компанії, підтримка)
  ├── COMPANY           — дії компанії / COMPANY_ADMIN / EMPLOYEE
  ├── STUDENT           — дії студента
  └── USER (спільне)    — профіль, запрошення, підтримка (для всіх авторизованих)
"""

import uuid
import threading
from flask import request, session, redirect, flash, jsonify, render_template
from repository.user_repository import (
    row_to_dict,
    UserRepository,
    StudentRepository,
    CompanyRepository,
    InvitationRepository,
    SupportRepository,
)


def register_routes(app):
    """Реєструє всі маршрути в переданий Flask-додаток."""

    # ══════════════════════════════════════════════════════════════════════
    # ДОПОМІЖНІ ФУНКЦІЇ
    # ══════════════════════════════════════════════════════════════════════

    def _merge_invitation(row):
        """Об'єднує Invitation + joined поля в один dict."""
        inv = row_to_dict(row[0])
        mapping = row._mapping
        for key in mapping.keys():
            if key != 'Invitation':
                inv[key] = mapping[key]
        return inv

    def render(active_tab='home', **kwargs):
        all_companies = kwargs.get('all_companies') or CompanyRepository.get_all_simple()

        unread_support_count = 0
        if session.get('role') == 'ADMIN':
            unread_support_count = SupportRepository.get_unread_count()

        return render_template(
            'index.html',
            active_tab=active_tab,
            students=kwargs.get('students', []),
            all_students=kwargs.get('all_students', []),
            all_companies=all_companies,
            user_info=kwargs.get('user_info', {}),
            profile_data=kwargs.get('profile_data', {}),
            invitations=kwargs.get('invitations', []),
            pending_count=kwargs.get('pending_count', 0),
            current_filters=kwargs.get('current_filters', {'search': '', 'course': '', 'specialty': '', 'sort': 'desc'}),
            unique_courses=kwargs.get('unique_courses', []),
            unique_specialties=kwargs.get('unique_specialties', []),
            unread_support_count=unread_support_count,
            support_conversations=kwargs.get('support_conversations', []),
            active_conv_key=kwargs.get('active_conv_key'),
            active_conv_messages=kwargs.get('active_conv_messages', []),
            active_conv_sender=kwargs.get('active_conv_sender'),
            show_archived=kwargs.get('show_archived', False),
            all_users=[]
        )

    # ══════════════════════════════════════════════════════════════════════
    # ГОЛОВНА СТОРІНКА / АВТОРИЗАЦІЯ
    # ══════════════════════════════════════════════════════════════════════

    @app.route('/')
    def index():
        from database import seed_default_admin
        seed_default_admin()

        if 'user_id' not in session:
            return render_template('index.html',
                active_tab='landing', students=[], all_students=[],
                all_companies=[], user_info={}, profile_data={},
                invitations=[], pending_count=0, current_filters={},
                unique_courses=[], unique_specialties=[],
                unread_support_count=0, support_conversations=[],
                active_conv_key=None, active_conv_messages=[],
                active_conv_sender=None, show_archived=False, all_users=[])

        active_tab = request.args.get('tab', 'home')

        # ── Фільтри рейтингу ──
        search_query     = request.args.get('search', '').strip()
        course_filter    = request.args.get('course', '').strip()
        specialty_filter = request.args.get('specialty', '').strip()
        sort_order       = request.args.get('sort', 'desc')
        current_filters  = {
            'search': search_query, 'course': course_filter,
            'specialty': specialty_filter, 'sort': sort_order
        }

        # ── Рейтинг студентів ──
        students, unique_courses, unique_specialties = [], [], []
        if active_tab == 'ranking':
            unique_courses     = StudentRepository.get_unique_courses()
            unique_specialties = StudentRepository.get_unique_specialties()
            students           = StudentRepository.get_filtered(
                search=search_query, course=course_filter,
                specialty=specialty_filter, sort=sort_order
            )

        # ── Адмін: студенти та компанії ──
        all_students, all_companies = [], []
        if session.get('role') == 'ADMIN':
            if active_tab == 'users':
                all_students = StudentRepository.get_all_ordered()
            if active_tab == 'companies':
                all_companies = CompanyRepository.get_all_with_employees()

        # ── Профіль ──
        user_info, profile_data = {}, {}
        if 'user_id' in session:
            target_id = session.get('edit_target_id', session['user_id'])
            role = session.get('role')

            if role == 'ADMIN':
                if session.get('edit_target_id'):
                    student = StudentRepository.get_by_id(target_id)
                    if student:
                        user_info = row_to_dict(student)
                        user_info['role'] = 'STUDENT'
                        profile_data = user_info
                    else:
                        user = UserRepository.get_user_by_id(target_id)
                        if user:
                            user_info = row_to_dict(user)
                            comp = CompanyRepository.get_by_id(user_info.get('company_id'))
                            profile_data = row_to_dict(comp) if comp else {}
                        else:
                            admin = UserRepository.get_admin_by_id(session['user_id'])
                            user_info = row_to_dict(admin) if admin else {}
                            user_info['role'] = 'ADMIN'
                            profile_data = user_info
                else:
                    admin = UserRepository.get_admin_by_id(target_id)
                    user_info = row_to_dict(admin) if admin else {}
                    user_info['role'] = 'ADMIN'
                    profile_data = user_info

            elif role == 'STUDENT':
                student = StudentRepository.get_by_id(target_id)
                user_info = row_to_dict(student) if student else {}
                user_info['role'] = 'STUDENT'
                profile_data = user_info

            else:
                user = UserRepository.get_user_by_id(target_id)
                user_info = row_to_dict(user) if user else {}
                comp = CompanyRepository.get_by_id(user_info.get('company_id'))
                profile_data = row_to_dict(comp) if comp else {}

        # ── Запрошення ──
        invitations, pending_count = [], 0
        role = session.get('role')

        if role == 'STUDENT':
            pending_count = InvitationRepository.get_pending_count(session['user_id'])

        if active_tab == 'invitations':
            if role == 'ADMIN':
                invitations = [_merge_invitation(r) for r in InvitationRepository.get_all_for_admin()]
            elif role in ('COMPANY_ADMIN', 'EMPLOYEE'):
                comp_id = session.get('company_id')
                if comp_id:
                    invitations = [_merge_invitation(r) for r in InvitationRepository.get_for_company(comp_id)]
            elif role == 'STUDENT':
                invitations = [_merge_invitation(r) for r in InvitationRepository.get_for_student(session['user_id'])]

        # ── Підтримка (лише Admin) ──
        support_conversations, active_conv_key, active_conv_messages, active_conv_sender = [], None, [], None
        show_archived = bool(request.args.get('show_archived'))

        if role == 'ADMIN' and active_tab == 'support':
            support_conversations = SupportRepository.get_conversations(archived=show_archived)
            active_conv_key = request.args.get('conv_key') or (
                support_conversations[0]['session_key'] if support_conversations else None
            )
            if active_conv_key:
                active_conv_messages = SupportRepository.get_messages(active_conv_key)
                SupportRepository.mark_read(active_conv_key, exclude_admin=True)
                active_conv_sender = SupportRepository.get_sender_name(active_conv_key)

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

    @app.route('/login', methods=['POST'])
    def login():
        login_input = (request.form.get('username') or '').strip()
        password    = request.form.get('password')

        obj, obj_type = UserRepository.find_by_login(login_input, password)

        if obj is None:
            flash("Невірні дані для входу")
            return redirect('/')

        if getattr(obj, 'status', None) == 'blocked':
            flash("Ваш акаунт заблоковано.")
            return redirect('/')

        if obj_type == 'admin':
            session.update({'user_id': obj.id, 'role': 'ADMIN',
                            'username': obj.username, 'company_id': None})
        elif obj_type == 'student':
            session.update({'user_id': obj.id, 'role': 'STUDENT',
                            'username': obj.username, 'company_id': None})
        else:
            session.update({'user_id': obj.id, 'role': obj.role,
                            'username': obj.username, 'company_id': obj.company_id})

        session.pop('edit_target_id', None)
        return redirect('/')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')

    # ══════════════════════════════════════════════════════════════════════
    # ADMIN — адміністратор
    # ══════════════════════════════════════════════════════════════════════

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

    @app.route('/admin/toggle_block', methods=['POST'])
    def admin_toggle_block():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        user_id   = request.form.get('user_id')
        user_type = request.form.get('user_type', 'employee')
        if user_type == 'student':
            StudentRepository.toggle_block(user_id)
            tab = 'users'
        else:
            UserRepository.toggle_block_user(user_id)
            tab = 'companies'
        flash("Статус змінено.")
        return redirect(f'/?tab={tab}')

    @app.route('/admin/delete_user', methods=['POST'])
    def admin_delete_user():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        user_id   = request.form.get('user_id')
        user_type = request.form.get('user_type', 'employee')
        if user_type == 'student':
            StudentRepository.delete(user_id)
            flash("Студента видалено.")
            return redirect('/?tab=users')
        else:
            UserRepository.delete_user(user_id)
            flash("Працівника видалено.")
            return redirect('/?tab=companies')

    @app.route('/admin/add_employee', methods=['POST'])
    def admin_add_employee():
        if session.get('role') != 'ADMIN':
            flash("Доступ заборонено.")
            return redirect('/')
        try:
            UserRepository.create_user(
                email=request.form.get('email', '').strip(),
                password=request.form.get('password', '').strip(),
                role='EMPLOYEE',
                company_id=request.form.get('company_id'),
                position=request.form.get('position', '').strip()
            )
            flash(f"Працівника '{request.form.get('email')}' додано до компанії!")
        except Exception as e:
            flash(f"Помилка: {e}")
        return redirect('/?tab=companies')

    @app.route('/admin/create_company', methods=['POST'])
    def admin_create_company():
        if session.get('role') != 'ADMIN':
            flash("Доступ заборонено.")
            return redirect('/')
        try:
            comp = CompanyRepository.create(
                company_name=request.form.get('company_name'),
                email=request.form.get('email'),
                password=request.form.get('password')
            )
            flash(f"Компанію '{comp.company_name}' створено! Логін директора: {request.form.get('email')}")
        except Exception as e:
            flash(f"Помилка: {e}")
        return redirect('/?tab=companies')

    @app.route('/admin/delete_company', methods=['POST'])
    def admin_delete_company():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        try:
            CompanyRepository.delete(request.form.get('company_id'))
            flash("Компанію видалено.")
        except Exception as e:
            flash(f"Помилка: {e}")
        return redirect('/?tab=companies')

    @app.route('/delete_invite', methods=['POST'])
    def delete_invite():
        if session.get('role') not in ('ADMIN', 'COMPANY_ADMIN', 'EMPLOYEE'):
            return redirect('/')
        invite_id = request.form.get('invite_id')
        inv = InvitationRepository.delete(invite_id)
        if not inv:
            return redirect('/?tab=invitations')
        if session.get('role') != 'ADMIN':
            if inv.company_id != session.get('company_id'):
                flash("Доступ заборонено.")
                return redirect('/?tab=invitations')
        flash("Заявку успішно видалено.")
        return redirect('/?tab=invitations')

    @app.route('/admin/support_reply', methods=['POST'])
    def admin_support_reply():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        conv_key = request.form.get('conv_key')
        reply    = request.form.get('reply')

        SupportRepository.mark_read(conv_key)
        SupportRepository.send_message(
            sender_type='admin', sender_id=session['user_id'],
            sender_name='Адміністратор', message=reply,
            conv_key=conv_key, is_read=1
        )

        from bot import tg_send, TG_GROUP
        threading.Thread(
            target=lambda: tg_send(
                TG_GROUP,
                f'✅ Відповідь надіслана через сайт у чат <code>{conv_key}</code>:\n{reply}'
            ),
            daemon=True
        ).start()

        flash("Відповідь надіслано!")
        return redirect(f'/?tab=support&conv_key={conv_key}')

    @app.route('/admin/support_archive', methods=['POST'])
    def admin_support_archive():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        conv_key = request.form.get('conv_key')
        action   = request.form.get('action', 'archive')
        SupportRepository.archive(conv_key, action)
        messages = {'archive': "Діалог переміщено в архів.", 'unarchive': "Діалог відновлено.", 'delete': "Діалог видалено назавжди."}
        flash(messages.get(action, ''))
        suffix = '&show_archived=1' if action == 'unarchive' else ''
        return redirect(f'/?tab=support{suffix}')

    # ══════════════════════════════════════════════════════════════════════
    # COMPANY — COMPANY_ADMIN / EMPLOYEE
    # ══════════════════════════════════════════════════════════════════════

    @app.route('/company/add_employee', methods=['POST'])
    def company_add_employee():
        if session.get('role') != 'COMPANY_ADMIN':
            flash("Доступ заборонено.")
            return redirect('/')
        company_id = session.get('company_id')
        if not company_id:
            flash("Не вдалося визначити вашу компанію.")
            return redirect('/')
        try:
            email = request.form.get('email', '').strip()
            UserRepository.create_user(
                email=email,
                password=request.form.get('password', '').strip(),
                role='EMPLOYEE',
                company_id=company_id,
                position=request.form.get('position', '').strip()
            )
            flash(f"Робітника '{email}' успішно додано!")
        except Exception as e:
            flash(f"Помилка: {e}")
        return redirect('/?tab=invitations')

    @app.route('/send_invite', methods=['POST'])
    def send_invite():
        if 'user_id' not in session:
            return redirect('/')
        user = UserRepository.get_user_by_id(session['user_id'])
        InvitationRepository.create(
            student_id=request.form.get('student_id'),
            company_id=user.company_id if user else None,
            user_id=session['user_id'],
            message=request.form.get('message')
        )
        flash("Запрошення надіслано!")
        return redirect('/?tab=ranking')

    # ══════════════════════════════════════════════════════════════════════
    # STUDENT — студент
    # ══════════════════════════════════════════════════════════════════════

    @app.route('/respond_invite', methods=['POST'])
    def respond_invite():
        if session.get('role') != 'STUDENT':
            return redirect('/')
        action     = request.form.get('action')
        new_status = 'accepted' if action == 'accept' else 'rejected'
        InvitationRepository.update_status(request.form.get('invite_id'), new_status)
        flash("Ви прийняли пропозицію!" if new_status == 'accepted' else "Ви відхилили пропозицію.")
        return redirect('/?tab=invitations')

    # ══════════════════════════════════════════════════════════════════════
    # USER (СПІЛЬНЕ) — всі авторизовані користувачі
    # ══════════════════════════════════════════════════════════════════════

    @app.route('/update_profile', methods=['POST'])
    def update_profile():
        if 'user_id' not in session:
            return redirect('/')
        target_id = session.get('edit_target_id', session['user_id'])
        role      = session.get('role')

        if target_id != session['user_id'] and role != 'ADMIN':
            return "Access Denied", 403

        # Визначаємо роль цільового користувача
        if role == 'ADMIN' and session.get('edit_target_id'):
            if StudentRepository.get_by_id(target_id):
                target_role = 'STUDENT'
            else:
                user = UserRepository.get_user_by_id(target_id)
                target_role = user.role if user else role
        else:
            target_role = role

        form = request.form
        if target_role == 'STUDENT':
            StudentRepository.update_profile(
                student_id=target_id,
                data=form,
                update_rating=(role == 'ADMIN')
            )
        elif target_role in ('COMPANY', 'COMPANY_ADMIN', 'EMPLOYEE'):
            user = UserRepository.get_user_by_id(target_id)
            if user and form.get('email') and role == 'ADMIN':
                UserRepository.update_user_profile(target_id, form.get('email'))
            if user and user.company_id:
                CompanyRepository.update_profile(user.company_id, form)

        flash("Профіль успішно оновлено!")
        return redirect('/?tab=profile')

    @app.route('/support/send', methods=['POST'])
    def support_send():
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

        SupportRepository.send_message(
            sender_type=sender_type, sender_id=sender_id,
            sender_name=sender_name, message=message,
            conv_key=conv_key, is_read=0
        )

        from bot import tg_notify_admin
        threading.Thread(
            target=lambda: tg_notify_admin(sender_name, conv_key, message),
            daemon=True
        ).start()

        return jsonify({'ok': True})

    @app.route('/support/history')
    def support_history():
        if 'user_id' in session:
            conv_key = f"user_{session['user_id']}"
        elif 'support_key' in session:
            conv_key = f"guest_{session['support_key']}"
        else:
            return jsonify([])

        msgs = SupportRepository.get_messages(conv_key)
        return jsonify([{
            'id': m['id'], 'sender_type': m['sender_type'],
            'sender_name': m['sender_name'], 'message': m['message'],
            'created_at': str(m['created_at'])
        } for m in msgs])

    @app.route('/support/check_new')
    def support_check_new():
        last_id = request.args.get('last_id', 0, type=int)
        if 'user_id' in session:
            conv_key = f"user_{session['user_id']}"
        elif 'support_key' in session:
            conv_key = f"guest_{session['support_key']}"
        else:
            return jsonify([])

        msgs = SupportRepository.get_new_messages(conv_key, last_id)
        result = [{'id': m.id, 'sender_type': m.sender_type,
                   'sender_name': m.sender_name, 'message': m.message,
                   'created_at': str(m.created_at)} for m in msgs]
        if result:
            SupportRepository.mark_read_by_ids([m['id'] for m in result])

        return jsonify(result)

    # ══════════════════════════════════════════════════════════════════════
    # API
    # ══════════════════════════════════════════════════════════════════════

    @app.route('/api/student/<int:user_id>')
    def get_student_api(user_id):
        student = StudentRepository.get_by_id(user_id)
        if student:
            return jsonify(row_to_dict(student))
        return jsonify({"error": "Student not found"}), 404
