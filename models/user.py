from models.db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    @staticmethod
    def create_user(email, password, role, name, phone=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, role, name, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (email.lower(), password_hash, role, name, phone))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except Exception as e:
            conn.close()
            return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email.lower(),)).fetchone()
        conn.close()
        return user

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return user

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

    @staticmethod
    def get_all():
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
        conn.close()
        return users
