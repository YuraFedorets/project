"""
database.py — Робота з базою даних через SQLAlchemy + Flask-Migrate.
Моделі побудовані точно за схемою ukd_database.db
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_extensions(app):
    """Ініціалізація SQLAlchemy та Flask-Migrate."""
    db.init_app(app)
    migrate.init_app(app, db)


def close_connection(exception):
    """Закриття сесії після кожного запиту."""
    db.session.remove()


# ── Моделі ────────────────────────────────────────────────────────────────────

class Admin(db.Model):
    __tablename__ = 'admins'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username    = db.Column(db.Text)
    email       = db.Column(db.Text)
    password    = db.Column(db.Text, default='123')
    status      = db.Column(db.Text, default='active')
    admin_level = db.Column(db.Integer, default=1)


class Company(db.Model):
    __tablename__ = 'companies'

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.Text, unique=True, nullable=False)
    description  = db.Column(db.Text)
    contact_info = db.Column(db.Text)
    avatar       = db.Column(db.Text, default='https://cdn-icons-png.flaticon.com/512/3061/3061341.png')
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'))
    position     = db.Column(db.Text)

    user         = db.relationship('User', foreign_keys=[user_id], back_populates='company_profile')
    invitations  = db.relationship('Invitation', back_populates='company', foreign_keys='Invitation.company_id')


class User(db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email      = db.Column(db.Text, unique=True, nullable=False)
    password   = db.Column(db.Text, nullable=False)
    role       = db.Column(db.Text, nullable=False, default='STUDENT')  # STUDENT | COMPANY_ADMIN | EMPLOYEE | ADMIN
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    position   = db.Column(db.Text)
    status     = db.Column(db.Text, default='active')
    username   = db.Column(db.Text)

    company_profile = db.relationship('Company', foreign_keys=[Company.user_id], back_populates='user')
    invitations     = db.relationship('Invitation', back_populates='user', foreign_keys='Invitation.user_id')


class Student(db.Model):
    __tablename__ = 'students'

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username     = db.Column(db.Text)
    email        = db.Column(db.Text)
    password     = db.Column(db.Text, default='123')
    status       = db.Column(db.Text, default='active')
    first_name   = db.Column(db.Text)
    last_name    = db.Column(db.Text)
    patronymic   = db.Column(db.Text)
    course       = db.Column(db.Text)
    specialty    = db.Column(db.Text)
    skills       = db.Column(db.Text)
    links        = db.Column(db.Text)
    contact_info = db.Column(db.Text)
    rating       = db.Column(db.Integer, default=0)
    avatar       = db.Column(db.Text, default='https://cdn-icons-png.flaticon.com/512/354/354637.png')

    invitations  = db.relationship('Invitation', back_populates='student', foreign_keys='Invitation.student_id')


class Invitation(db.Model):
    __tablename__ = 'invitations'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    message    = db.Column(db.Text)
    status     = db.Column(db.Text, default='pending')
    flagged    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    student    = db.relationship('Student', back_populates='invitations', foreign_keys=[student_id])
    company    = db.relationship('Company', back_populates='invitations', foreign_keys=[company_id])
    user       = db.relationship('User',    back_populates='invitations', foreign_keys=[user_id])


class SupportMessage(db.Model):
    __tablename__ = 'support_messages'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_type = db.Column(db.Text, nullable=False)  # 'guest' | 'student' | 'company' | 'admin'
    sender_id   = db.Column(db.Integer)
    sender_name = db.Column(db.Text)
    message     = db.Column(db.Text, nullable=False)
    reply       = db.Column(db.Text)
    replied_at  = db.Column(db.DateTime)
    session_key = db.Column(db.Text)
    is_read     = db.Column(db.Integer, default=0)
    is_archived = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, server_default=db.func.current_timestamp())


# ── Seed: дефолтний адмін ─────────────────────────────────────────────────────

def seed_default_admin():
    """Створює адміна за замовчуванням, якщо його ще немає."""
    if not Admin.query.filter_by(username='admin').first():
        db.session.add(Admin(
            username    = 'admin',
            email       = 'admin@ukd.edu.ua',
            password    = '123',
            admin_level = 10
        ))
        db.session.commit()
