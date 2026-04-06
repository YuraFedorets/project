"""
repository/user_repository.py — Repository Pattern для УКД Talent.
Містить всю логіку роботи з БД, винесену з routes.py.

Використання в routes.py:
    from repository.user_repository import UserRepository, StudentRepository,
        CompanyRepository, InvitationRepository, SupportRepository
"""

from database import db
from models.user import Admin, User, Student, Company, Invitation, SupportMessage


# ── Допоміжна функція ─────────────────────────────────────────────────────────

def row_to_dict(obj) -> dict:
    """Конвертує SQLAlchemy об'єкт у dict."""
    d = obj.__dict__.copy()
    d.pop('_sa_instance_state', None)
    return d


# ══════════════════════════════════════════════════════════════════════════════
# UserRepository — авторизація, пошук по всіх таблицях
# ══════════════════════════════════════════════════════════════════════════════

class UserRepository:

    @staticmethod
    def find_by_login(login: str, password: str) -> tuple:
        """
        Шукає користувача по логіну/паролю в Admin → Student → User.
        Повертає (об'єкт, тип) або (None, None).
        """
        admin = Admin.query.filter(
            db.or_(Admin.username == login, Admin.email == login),
            Admin.password == password
        ).first()
        if admin:
            return admin, 'admin'

        student = Student.query.filter(
            db.or_(Student.username == login, Student.email == login),
            Student.password == password
        ).first()
        if student:
            return student, 'student'

        user = User.query.filter(
            db.or_(User.username == login, User.email == login),
            User.password == password
        ).first()
        if user:
            return user, 'user'

        return None, None

    @staticmethod
    def get_admin_by_id(admin_id: int) -> Admin | None:
        return Admin.query.get(admin_id)

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return User.query.get(user_id)

    @staticmethod
    def create_user(email: str, password: str, role: str,
                    company_id: int = None, position: str = None) -> User:
        user = User(
            username=email, email=email, password=password,
            role=role, company_id=company_id,
            position=position, status='active'
        )
        db.session.add(user)
        db.session.flush()  # отримуємо id без commit
        return user

    @staticmethod
    def delete_user(user_id: int) -> None:
        Invitation.query.filter_by(user_id=user_id).delete()
        User.query.filter_by(id=user_id).delete()
        db.session.commit()

    @staticmethod
    def toggle_block_user(user_id: int) -> str:
        """Перемикає статус active/blocked. Повертає новий статус."""
        user = User.query.get(user_id)
        if user:
            user.status = 'active' if user.status == 'blocked' else 'blocked'
            db.session.commit()
            return user.status
        return None

    @staticmethod
    def update_user_profile(user_id: int, email: str) -> None:
        user = User.query.get(user_id)
        if user:
            user.email    = email
            user.username = email
            db.session.commit()


# ══════════════════════════════════════════════════════════════════════════════
# StudentRepository — робота зі студентами
# ══════════════════════════════════════════════════════════════════════════════

class StudentRepository:

    @staticmethod
    def get_by_id(student_id: int) -> Student | None:
        return Student.query.get(student_id)

    @staticmethod
    def get_all_ordered() -> list[dict]:
        return [row_to_dict(s) for s in Student.query.order_by(Student.last_name).all()]

    @staticmethod
    def get_filtered(search: str = '', course: str = '',
                     specialty: str = '', sort: str = 'desc') -> list[dict]:
        """Фільтрований список студентів для рейтингу."""
        q = Student.query.filter(Student.status != 'blocked')

        if search:
            like = f'%{search}%'
            q = q.filter(db.or_(
                Student.first_name.like(like),
                Student.last_name.like(like),
                Student.skills.like(like),
                Student.specialty.like(like)
            ))
        if course:
            q = q.filter(Student.course == course)
        if specialty:
            q = q.filter(Student.specialty == specialty)

        q = q.order_by(Student.rating.asc() if sort == 'asc' else Student.rating.desc())
        return [row_to_dict(s) for s in q.all()]

    @staticmethod
    def get_unique_courses() -> list[str]:
        return [r[0] for r in db.session.query(Student.course).filter(
            Student.course.isnot(None), Student.course != ''
        ).distinct().order_by(Student.course).all()]

    @staticmethod
    def get_unique_specialties() -> list[str]:
        return [r[0] for r in db.session.query(Student.specialty).filter(
            Student.specialty.isnot(None), Student.specialty != ''
        ).distinct().order_by(Student.specialty).all()]

    @staticmethod
    def update_profile(student_id: int, data: dict, update_rating: bool = False) -> None:
        """
        Оновлює профіль студента.
        data — dict з полями форми. update_rating=True тільки для ADMIN.
        """
        student = Student.query.get(student_id)
        if not student:
            return
        if update_rating and data.get('rating') is not None:
            student.rating = int(data['rating'])

        student.first_name   = data.get('first_name')
        student.last_name    = data.get('last_name')
        student.patronymic   = data.get('patronymic')
        student.course       = data.get('course')
        student.specialty    = data.get('specialty')
        student.skills       = data.get('skills')
        student.links        = data.get('links')
        student.contact_info = data.get('contact_info')
        student.avatar       = data.get('avatar')
        student.email        = data.get('email')
        student.username     = data.get('email')
        db.session.commit()

    @staticmethod
    def toggle_block(student_id: int) -> str:
        """Перемикає статус active/blocked. Повертає новий статус."""
        student = Student.query.get(student_id)
        if student:
            student.status = 'active' if student.status == 'blocked' else 'blocked'
            db.session.commit()
            return student.status
        return None

    @staticmethod
    def delete(student_id: int) -> None:
        Invitation.query.filter_by(student_id=student_id).delete()
        Student.query.filter_by(id=student_id).delete()
        db.session.commit()


# ══════════════════════════════════════════════════════════════════════════════
# CompanyRepository — робота з компаніями та їх профілями
# ══════════════════════════════════════════════════════════════════════════════

class CompanyRepository:

    @staticmethod
    def get_by_id(company_id: int) -> Company | None:
        return Company.query.get(company_id)

    @staticmethod
    def get_all_with_employees() -> list[dict]:
        """Повний список компаній з працівниками (для адмін-панелі)."""
        result = []
        for comp in Company.query.order_by(Company.company_name).all():
            c = row_to_dict(comp)
            c['employees'] = [row_to_dict(e) for e in
                User.query.filter_by(company_id=comp.id)
                .order_by(User.role, User.username).all()]
            result.append(c)
        return result

    @staticmethod
    def get_all_simple() -> list[dict]:
        """Список компаній без деталей (для дропдаунів)."""
        result = []
        for comp in Company.query.order_by(Company.company_name).all():
            c = row_to_dict(comp)
            c['employees'] = []
            result.append(c)
        return result

    @staticmethod
    def create(company_name: str, email: str, password: str) -> Company:
        """Створює компанію та COMPANY_ADMIN користувача. Повертає об'єкт компанії."""
        comp = Company(company_name=company_name)
        db.session.add(comp)
        db.session.flush()

        user = User(username=email, email=email, password=password,
                    role='COMPANY_ADMIN', company_id=comp.id,
                    position='Директор', status='active')
        db.session.add(user)
        db.session.flush()

        comp.user_id = user.id
        db.session.commit()
        return comp

    @staticmethod
    def delete(company_id: int) -> None:
        """Каскадне видалення компанії разом з усіма юзерами та запрошеннями."""
        users = User.query.filter_by(company_id=company_id).all()
        for u in users:
            Invitation.query.filter_by(user_id=u.id).delete()
        User.query.filter_by(company_id=company_id).delete()
        Invitation.query.filter_by(company_id=company_id).delete()
        Company.query.filter_by(id=company_id).delete()
        db.session.commit()

    @staticmethod
    def update_profile(company_id: int, data: dict) -> None:
        comp = Company.query.get(company_id)
        if not comp:
            return
        comp.company_name = data.get('company_name')
        comp.description  = data.get('description')
        comp.avatar       = data.get('avatar')
        comp.position     = data.get('position')
        comp.contact_info = data.get('contact_info')
        db.session.commit()


# ══════════════════════════════════════════════════════════════════════════════
# InvitationRepository — запрошення студентів
# ══════════════════════════════════════════════════════════════════════════════

class InvitationRepository:

    @staticmethod
    def get_all_for_admin() -> list:
        """Всі запрошення з joined даними для адмін-панелі."""
        return db.session.query(
            Invitation,
            Student.first_name, Student.last_name,
            Company.company_name, Company.avatar.label('company_avatar')
        ).outerjoin(Student, Invitation.student_id == Student.id)\
         .outerjoin(Company, Invitation.company_id == Company.id)\
         .order_by(Invitation.created_at.desc()).all()

    @staticmethod
    def get_for_company(company_id: int) -> list:
        """Запрошення конкретної компанії."""
        return db.session.query(
            Invitation,
            Student.first_name, Student.last_name,
            Company.company_name, Company.avatar.label('company_avatar')
        ).join(Student, Invitation.student_id == Student.id)\
         .outerjoin(Company, Invitation.company_id == Company.id)\
         .filter(Invitation.company_id == company_id)\
         .order_by(Invitation.created_at.desc()).all()

    @staticmethod
    def get_for_student(student_id: int) -> list:
        """Запрошення конкретного студента."""
        return db.session.query(
            Invitation,
            Company.company_name, Company.avatar.label('company_avatar')
        ).outerjoin(Company, Invitation.company_id == Company.id)\
         .filter(Invitation.student_id == student_id)\
         .order_by(Invitation.created_at.desc()).all()

    @staticmethod
    def get_pending_count(student_id: int) -> int:
        return Invitation.query.filter_by(student_id=student_id, status='pending').count()

    @staticmethod
    def create(student_id: int, company_id: int, user_id: int, message: str) -> Invitation:
        inv = Invitation(
            student_id=student_id, company_id=company_id,
            user_id=user_id, message=message, status='pending'
        )
        db.session.add(inv)
        db.session.commit()
        return inv

    @staticmethod
    def update_status(invite_id: int, status: str) -> bool:
        inv = Invitation.query.get(invite_id)
        if inv:
            inv.status = status
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete(invite_id: int) -> Invitation | None:
        """Видаляє запрошення. Повертає об'єкт або None якщо не знайдено."""
        inv = Invitation.query.get(invite_id)
        if inv:
            db.session.delete(inv)
            db.session.commit()
        return inv


# ══════════════════════════════════════════════════════════════════════════════
# SupportRepository — повідомлення підтримки
# ══════════════════════════════════════════════════════════════════════════════

class SupportRepository:

    @staticmethod
    def get_unread_count() -> int:
        """Кількість непрочитаних повідомлень (для бейджа в меню)."""
        return SupportMessage.query.filter_by(
            is_read=0, is_archived=0
        ).filter(SupportMessage.sender_type != 'admin').count()

    @staticmethod
    def get_conversations(archived: bool = False) -> list[dict]:
        """Список діалогів для адмін-панелі підтримки."""
        rows = db.session.execute(db.text("""
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
        """), {'archived': 1 if archived else 0}).fetchall()
        return [dict(r._mapping) for r in rows]

    @staticmethod
    def get_messages(conv_key: str) -> list[dict]:
        msgs = SupportMessage.query.filter_by(session_key=conv_key)\
            .order_by(SupportMessage.created_at.asc()).all()
        return [row_to_dict(m) for m in msgs]

    @staticmethod
    def get_new_messages(conv_key: str, last_id: int) -> list[SupportMessage]:
        """Нові непрочитані відповіді адміна для polling'у з боку юзера."""
        return SupportMessage.query.filter(
            SupportMessage.session_key == conv_key,
            SupportMessage.id > last_id,
            SupportMessage.sender_type == 'admin',
            SupportMessage.is_read == 0
        ).order_by(SupportMessage.created_at.asc()).all()

    @staticmethod
    def get_sender_name(conv_key: str) -> str:
        row = SupportMessage.query.filter(
            SupportMessage.session_key == conv_key,
            SupportMessage.sender_type != 'admin'
        ).first()
        return row.sender_name if row else 'Гість'

    @staticmethod
    def send_message(sender_type: str, sender_id: int, sender_name: str,
                     message: str, conv_key: str, is_read: int = 0) -> SupportMessage:
        msg = SupportMessage(
            sender_type=sender_type, sender_id=sender_id,
            sender_name=sender_name, message=message,
            session_key=conv_key, is_read=is_read
        )
        db.session.add(msg)
        db.session.commit()
        return msg

    @staticmethod
    def mark_read(conv_key: str, exclude_admin: bool = False) -> None:
        q = SupportMessage.query.filter_by(session_key=conv_key)
        if exclude_admin:
            q = q.filter(SupportMessage.sender_type != 'admin')
        q.update({'is_read': 1})
        db.session.commit()

    @staticmethod
    def mark_read_by_ids(ids: list[int]) -> None:
        SupportMessage.query.filter(SupportMessage.id.in_(ids))\
            .update({'is_read': 1}, synchronize_session=False)
        db.session.commit()

    @staticmethod
    def archive(conv_key: str, action: str) -> None:
        """action: 'archive' | 'unarchive' | 'delete'"""
        if action == 'archive':
            SupportMessage.query.filter_by(session_key=conv_key).update({'is_archived': 1})
        elif action == 'unarchive':
            SupportMessage.query.filter_by(session_key=conv_key).update({'is_archived': 0})
        elif action == 'delete':
            SupportMessage.query.filter_by(session_key=conv_key).delete()
        db.session.commit()
