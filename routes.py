"""
routes.py — Всі Flask маршрути проекту УКД Talent.
Використовує SQLAlchemy замість прямих sqlite3 запитів.
"""

import uuid
import threading
from flask import request, session, redirect, flash, jsonify, render_template
from database import db, Admin, Company, User, Student, Invitation, SupportMessage


def register_routes(app):
    """Реєструє всі маршрути в переданий Flask-додаток."""

    # ── Допоміжна функція рендеру ──────────────────────────────────────────────
    def render(active_tab='home', **kwargs):
        students           = kwargs.get('students', [])
        current_filters    = kwargs.get('current_filters', {'search': '', 'course': '', 'specialty': '', 'sort': 'desc'})
        unique_courses     = kwargs.get('unique_courses', [])
        unique_specialties = kwargs.get('unique_specialties', [])
        all_students       = kwargs.get('all_students', [])

        all_companies = kwargs.get('all_companies', [])
        if not all_companies:
            for comp in Company.query.order_by(Company.company_name).all():
                c = comp.__dict__.copy()
                c.pop('_sa_instance_state', None)
                c['employees'] = []
                all_companies.append(c)

        user_info            = kwargs.get('user_info', {})
        profile_data         = kwargs.get('profile_data', {})
        invitations          = kwargs.get('invitations', [])
        pending_count        = kwargs.get('pending_count', 0)
        unread_support_count = 0
        support_conversations  = kwargs.get('support_conversations', [])
        active_conv_key        = kwargs.get('active_conv_key', None)
        active_conv_messages   = kwargs.get('active_conv_messages', [])
        active_conv_sender     = kwargs.get('active_conv_sender', None)
        show_archived          = kwargs.get('show_archived', False)

        if session.get('role') == 'ADMIN':
            unread_support_count = SupportMessage.query.filter_by(
                is_read=0, is_archived=0
            ).filter(SupportMessage.sender_type != 'admin').count()

        return render_template(
            'index.html',
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

    def row_to_dict(obj):
        """Конвертує SQLAlchemy об'єкт у dict."""
        d = obj.__dict__.copy()
        d.pop('_sa_instance_state', None)
        return d

    # ══════════════════════════════════════════════════════════════════════
    # ГОЛОВНА СТОРІНКА
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

        unique_courses, unique_specialties = [], []
        if active_tab == 'ranking':
            unique_courses = [r[0] for r in db.session.query(Student.course).filter(
                Student.course.isnot(None), Student.course != ''
            ).distinct().order_by(Student.course).all()]
            unique_specialties = [r[0] for r in db.session.query(Student.specialty).filter(
                Student.specialty.isnot(None), Student.specialty != ''
            ).distinct().order_by(Student.specialty).all()]

        # ── Список студентів ──
        students = []
        if active_tab == 'ranking':
            q = Student.query.filter(Student.status != 'blocked')
            if search_query:
                like = f'%{search_query}%'
                q = q.filter(
                    db.or_(Student.first_name.like(like), Student.last_name.like(like),
                           Student.skills.like(like), Student.specialty.like(like))
                )
            if course_filter:
                q = q.filter(Student.course == course_filter)
            if specialty_filter:
                q = q.filter(Student.specialty == specialty_filter)
            q = q.order_by(Student.rating.asc() if sort_order == 'asc' else Student.rating.desc())
            students = [row_to_dict(s) for s in q.all()]

        # ── Адмін: студенти та компанії ──
        all_students, all_companies = [], []
        if active_tab in ('users', 'companies') and session.get('role') == 'ADMIN':
            all_students = [row_to_dict(s) for s in Student.query.order_by(Student.last_name).all()]
            for comp in Company.query.order_by(Company.company_name).all():
                c = row_to_dict(comp)
                c['employees'] = [row_to_dict(e) for e in
                    User.query.filter_by(company_id=comp.id).order_by(User.role, User.username).all()]
                all_companies.append(c)
        if not all_companies:
            for comp in Company.query.order_by(Company.company_name).all():
                c = row_to_dict(comp)
                c['employees'] = []
                all_companies.append(c)

        # ── Профіль ──
        user_info, profile_data = {}, {}
        if 'user_id' in session:
            target_id = session.get('edit_target_id', session['user_id'])
            role = session.get('role')

            if role == 'ADMIN':
                if session.get('edit_target_id'):
                    row = Student.query.get(target_id)
                    if row:
                        user_info = row_to_dict(row)
                        user_info['role'] = 'STUDENT'
                        profile_data = user_info
                    else:
                        row = User.query.get(target_id)
                        if row:
                            user_info = row_to_dict(row)
                            comp = Company.query.get(user_info.get('company_id'))
                            profile_data = row_to_dict(comp) if comp else {}
                        else:
                            row = Admin.query.get(session['user_id'])
                            user_info = row_to_dict(row) if row else {}
                            user_info['role'] = 'ADMIN'
                            profile_data = user_info
                else:
                    row = Admin.query.get(target_id)
                    user_info = row_to_dict(row) if row else {}
                    user_info['role'] = 'ADMIN'
                    profile_data = user_info

            elif role == 'STUDENT':
                row = Student.query.get(target_id)
                user_info = row_to_dict(row) if row else {}
                user_info['role'] = 'STUDENT'
                profile_data = user_info

            else:
                row = User.query.get(target_id)
                user_info = row_to_dict(row) if row else {}
                comp_id = user_info.get('company_id')
                if comp_id:
                    comp = Company.query.get(comp_id)
                    profile_data = row_to_dict(comp) if comp else {}

        # ── Запрошення ──
        invitations, pending_count = [], 0
        if session.get('role') == 'STUDENT':
            pending_count = Invitation.query.filter_by(
                student_id=session['user_id'], status='pending'
            ).count()

        if active_tab == 'invitations':
            role = session.get('role')
            if role == 'ADMIN':
                rows = db.session.query(
                    Invitation, Student.first_name, Student.last_name,
                    Company.company_name, Company.avatar.label('company_avatar')
                ).outerjoin(Student, Invitation.student_id == Student.id)\
                 .outerjoin(Company, Invitation.company_id == Company.id)\
                 .order_by(Invitation.created_at.desc()).all()
                invitations = [_merge_invitation(r) for r in rows]

            elif role in ('COMPANY_ADMIN', 'EMPLOYEE'):
                comp_id = session.get('company_id')
                if comp_id:
                    rows = db.session.query(
                        Invitation, Student.first_name, Student.last_name,
                        Company.company_name, Company.avatar.label('company_avatar')
                    ).join(Student, Invitation.student_id == Student.id)\
                     .outerjoin(Company, Invitation.company_id == Company.id)\
                     .filter(Invitation.company_id == comp_id)\
                     .order_by(Invitation.created_at.desc()).all()
                    invitations = [_merge_invitation(r) for r in rows]

            elif role == 'STUDENT':
                rows = db.session.query(
                    Invitation, Company.company_name, Company.avatar.label('company_avatar')
                ).outerjoin(Company, Invitation.company_id == Company.id)\
                 .filter(Invitation.student_id == session['user_id'])\
                 .order_by(Invitation.created_at.desc()).all()
                invitations = [_merge_invitation(r) for r in rows]

        # ── Підтримка (Admin) ──
        support_conversations, active_conv_key, active_conv_messages, active_conv_sender = [], None, [], None
        show_archived = bool(request.args.get('show_archived'))

        if session.get('role') == 'ADMIN' and active_tab == 'support':
            convs = db.session.execute(db.text("""
                SELECT session_key, sender_name,
                       MAX(created_at) as last_time,
                       (SELECT message FROM support_messages sm2
                        WHERE sm2.session_key = sm.session_key
                        ORDER BY sm2.created_at DESC LIMIT 1) as last_message,
                       SUM(CASE WHEN is_read=0 AND sender_type != 'admin' THEN 1 ELSE 0 END) as unread_count
                FROM support_messages sm
                WHERE sender_type != 'admin'
                  AND is_archived = :archived
                GROUP BY session_key
                ORDER BY last_time DESC
            """), {'archived': 1 if show_archived else 0}).fetchall()
            support_conversations = [dict(c._mapping) for c in convs]

            active_conv_key = request.args.get('conv_key') or (
                support_conversations[0]['session_key'] if support_conversations else None
            )
            if active_conv_key:
                active_conv_messages = [row_to_dict(m) for m in
                    SupportMessage.query.filter_by(session_key=active_conv_key)
                    .order_by(SupportMessage.created_at.asc()).all()]

                SupportMessage.query.filter(
                    SupportMessage.session_key == active_conv_key,
                    SupportMessage.sender_type != 'admin'
                ).update({'is_read': 1})
                db.session.commit()

                sender_row = SupportMessage.query.filter(
                    SupportMessage.session_key == active_conv_key,
                    SupportMessage.sender_type != 'admin'
                ).first()
                active_conv_sender = sender_row.sender_name if sender_row else 'Гість'

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

    def _merge_invitation(row):
        """Об'єднує Invitation + joined поля в один dict."""
        inv = row_to_dict(row[0])
        for val in row[1:]:
            pass
        mapping = row._mapping
        for key in mapping.keys():
            if key != 'Invitation':
                inv[key] = mapping[key]
        return inv

    # ══════════════════════════════════════════════════════════════════════
    # АВТОРИЗАЦІЯ
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/login', methods=['POST'])
    def login():
        login_input = (request.form.get('username') or '').strip()
        password    = request.form.get('password')

        admin = Admin.query.filter(
            db.or_(Admin.username == login_input, Admin.email == login_input),
            Admin.password == password
        ).first()
        if admin:
            if admin.status == 'blocked':
                flash("Ваш акаунт заблоковано.")
                return redirect('/')
            session.update({'user_id': admin.id, 'role': 'ADMIN',
                            'username': admin.username, 'company_id': None})
            session.pop('edit_target_id', None)
            return redirect('/')

        student = Student.query.filter(
            db.or_(Student.username == login_input, Student.email == login_input),
            Student.password == password
        ).first()
        if student:
            if student.status == 'blocked':
                flash("Ваш акаунт заблоковано.")
                return redirect('/')
            session.update({'user_id': student.id, 'role': 'STUDENT',
                            'username': student.username, 'company_id': None})
            session.pop('edit_target_id', None)
            return redirect('/')

        user = User.query.filter(
            db.or_(User.username == login_input, User.email == login_input),
            User.password == password
        ).first()
        if user:
            if user.status == 'blocked':
                flash("Ваш акаунт заблоковано.")
                return redirect('/')
            session.update({'user_id': user.id, 'role': user.role,
                            'username': user.username, 'company_id': user.company_id})
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

        role = session.get('role')

        if role == 'ADMIN' and session.get('edit_target_id'):
            if Student.query.get(target_id):
                target_role = 'STUDENT'
            else:
                row = User.query.get(target_id)
                target_role = row.role if row else role
        else:
            target_role = role

        if target_role == 'STUDENT':
            student = Student.query.get(target_id)
            if student:
                if role == 'ADMIN':
                    rating_val = request.form.get('rating')
                    if rating_val is not None:
                        student.rating = int(rating_val)
                new_email = request.form.get('email')
                student.first_name   = request.form.get('first_name')
                student.last_name    = request.form.get('last_name')
                student.patronymic   = request.form.get('patronymic')
                student.course       = request.form.get('course')
                student.specialty    = request.form.get('specialty')
                student.skills       = request.form.get('skills')
                student.links        = request.form.get('links')
                student.contact_info = request.form.get('contact_info')
                student.avatar       = request.form.get('avatar')
                student.email        = new_email
                student.username     = new_email

        elif target_role in ('COMPANY', 'COMPANY_ADMIN', 'EMPLOYEE'):
            new_email = request.form.get('email')
            user = User.query.get(target_id)
            if user and new_email and role == 'ADMIN':
                user.email    = new_email
                user.username = new_email
            if user and user.company_id:
                comp = Company.query.get(user.company_id)
                if comp:
                    comp.company_name = request.form.get('company_name')
                    comp.description  = request.form.get('description')
                    comp.avatar       = request.form.get('avatar')
                    comp.position     = request.form.get('position')
                    comp.contact_info = request.form.get('contact_info')

        db.session.commit()
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
        student_id = request.form.get('student_id')
        message    = request.form.get('message')
        user = User.query.get(session['user_id'])
        comp_id = user.company_id if user else None
        db.session.add(Invitation(
            student_id=student_id, company_id=comp_id,
            user_id=session['user_id'], message=message, status='pending'
        ))
        db.session.commit()
        flash("Запрошення надіслано!")
        return redirect('/?tab=ranking')

    @app.route('/respond_invite', methods=['POST'])
    def respond_invite():
        if session.get('role') != 'STUDENT':
            return redirect('/')
        invite_id  = request.form.get('invite_id')
        action     = request.form.get('action')
        new_status = 'accepted' if action == 'accept' else 'rejected'
        inv = Invitation.query.get(invite_id)
        if inv:
            inv.status = new_status
            db.session.commit()
        flash("Ви прийняли пропозицію!" if new_status == 'accepted' else "Ви відхилили пропозицію.")
        return redirect('/?tab=invitations')

    @app.route('/delete_invite', methods=['POST'])
    def delete_invite():
        if session.get('role') not in ('ADMIN', 'COMPANY_ADMIN', 'EMPLOYEE'):
            return redirect('/')
        invite_id = request.form.get('invite_id')
        inv = Invitation.query.get(invite_id)
        if not inv:
            return redirect('/?tab=invitations')
        if session.get('role') != 'ADMIN':
            if inv.company_id != session.get('company_id'):
                flash("Доступ заборонено.")
                return redirect('/?tab=invitations')
        db.session.delete(inv)
        db.session.commit()
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
        if user_type == 'student':
            obj = Student.query.get(user_id)
            tab = 'users'
        else:
            obj = User.query.get(user_id)
            tab = 'companies'
        if obj:
            obj.status = 'active' if obj.status == 'blocked' else 'blocked'
            db.session.commit()
        flash("Статус змінено.")
        return redirect(f'/?tab={tab}')

    @app.route('/admin/delete_user', methods=['POST'])
    def admin_delete_user():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        user_id   = request.form.get('user_id')
        user_type = request.form.get('user_type', 'employee')
        if user_type == 'student':
            Invitation.query.filter_by(student_id=user_id).delete()
            Student.query.filter_by(id=user_id).delete()
            db.session.commit()
            flash("Студента видалено.")
            return redirect('/?tab=users')
        else:
            Invitation.query.filter_by(user_id=user_id).delete()
            User.query.filter_by(id=user_id).delete()
            db.session.commit()
            flash("Працівника видалено.")
            return redirect('/?tab=companies')

    @app.route('/admin/create_company', methods=['POST'])
    def admin_create_company():
        if session.get('role') != 'ADMIN':
            flash("Доступ заборонено.")
            return redirect('/')
        company_name = request.form.get('company_name')
        email        = request.form.get('email')
        password     = request.form.get('password')
        try:
            comp = Company(company_name=company_name)
            db.session.add(comp)
            db.session.flush()  # отримуємо comp.id без commit

            user = User(username=email, email=email, password=password,
                        role='COMPANY_ADMIN', company_id=comp.id,
                        position='Директор', status='active')
            db.session.add(user)
            db.session.flush()

            comp.user_id = user.id
            db.session.commit()
            flash(f"Компанію '{company_name}' створено! Логін директора: {email}")
        except Exception as e:
            db.session.rollback()
            flash(f"Помилка: {e}")
        return redirect('/?tab=companies')

    @app.route('/admin/add_employee', methods=['POST'])
    def admin_add_employee():
        if session.get('role') != 'ADMIN':
            flash("Доступ заборонено.")
            return redirect('/')
        email      = request.form.get('email', '').strip()
        position   = request.form.get('position', '').strip()
        password   = request.form.get('password', '').strip()
        company_id = request.form.get('company_id')
        try:
            db.session.add(User(username=email, email=email, password=password,
                                role='EMPLOYEE', company_id=company_id,
                                position=position, status='active'))
            db.session.commit()
            flash(f"Працівника '{email}' додано до компанії!")
        except Exception as e:
            db.session.rollback()
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
        try:
            db.session.add(User(username=email, email=email, password=password,
                                role='EMPLOYEE', company_id=company_id,
                                position=position, status='active'))
            db.session.commit()
            flash(f"Робітника '{email}' успішно додано!")
        except Exception as e:
            db.session.rollback()
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
        if action == 'archive':
            SupportMessage.query.filter_by(session_key=conv_key).update({'is_archived': 1})
            flash("Діалог переміщено в архів.")
        elif action == 'unarchive':
            SupportMessage.query.filter_by(session_key=conv_key).update({'is_archived': 0})
            flash("Діалог відновлено.")
        elif action == 'delete':
            SupportMessage.query.filter_by(session_key=conv_key).delete()
            flash("Діалог видалено назавжди.")
        db.session.commit()
        suffix = '&show_archived=1' if action == 'unarchive' else ''
        return redirect(f'/?tab=support{suffix}')

    @app.route('/admin/support_reply', methods=['POST'])
    def admin_support_reply():
        if session.get('role') != 'ADMIN':
            return redirect('/')
        conv_key = request.form.get('conv_key')
        reply    = request.form.get('reply')

        SupportMessage.query.filter_by(session_key=conv_key).update({'is_read': 1})
        db.session.add(SupportMessage(
            sender_type='admin', sender_id=session['user_id'],
            sender_name='Адміністратор', message=reply,
            session_key=conv_key, is_read=1
        ))
        db.session.commit()

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

        db.session.add(SupportMessage(
            sender_type=sender_type, sender_id=sender_id,
            sender_name=sender_name, message=message,
            session_key=conv_key, is_read=0
        ))
        db.session.commit()

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
        msgs = SupportMessage.query.filter_by(session_key=conv_key)\
            .order_by(SupportMessage.created_at.asc()).all()
        return jsonify([{
            'id': m.id, 'sender_type': m.sender_type,
            'sender_name': m.sender_name, 'message': m.message,
            'created_at': str(m.created_at)
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

        msgs = SupportMessage.query.filter(
            SupportMessage.session_key == conv_key,
            SupportMessage.id > last_id,
            SupportMessage.sender_type == 'admin',
            SupportMessage.is_read == 0
        ).order_by(SupportMessage.created_at.asc()).all()

        result = [{'id': m.id, 'sender_type': m.sender_type,
                   'sender_name': m.sender_name, 'message': m.message,
                   'created_at': str(m.created_at)} for m in msgs]
        if result:
            ids = [m['id'] for m in result]
            SupportMessage.query.filter(SupportMessage.id.in_(ids)).update(
                {'is_read': 1}, synchronize_session=False
            )
            db.session.commit()

        return jsonify(result)

    # ══════════════════════════════════════════════════════════════════════
    # API
    # ══════════════════════════════════════════════════════════════════════
    @app.route('/api/student/<int:user_id>')
    def get_student_api(user_id):
        student = Student.query.get(user_id)
        if student:
            return jsonify(row_to_dict(student))
        return jsonify({"error": "Student not found"}), 404
