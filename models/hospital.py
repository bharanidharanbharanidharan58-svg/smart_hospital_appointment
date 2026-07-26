from models.db import get_db_connection

class HospitalModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        hospitals = conn.execute('SELECT * FROM hospitals ORDER BY id ASC').fetchall()
        conn.close()
        return hospitals

    @staticmethod
    def get_by_id(hospital_id):
        conn = get_db_connection()
        hospital = conn.execute('SELECT * FROM hospitals WHERE id = ?', (hospital_id,)).fetchone()
        conn.close()
        return hospital

    @staticmethod
    def get_by_code(code):
        conn = get_db_connection()
        hospital = conn.execute('SELECT * FROM hospitals WHERE code = ?', (code,)).fetchone()
        conn.close()
        return hospital

    @staticmethod
    def create(name, code, logo, banner, address, city, phone, email, departments, working_hours, emergency_contact, rating=4.8, total_beds=250, total_doctors=25, about=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hospitals (name, code, logo, banner, address, city, phone, email, departments, working_hours, emergency_contact, rating, total_beds, total_doctors, about)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, code, logo, banner, address, city, phone, email, departments, working_hours, emergency_contact, rating, total_beds, total_doctors, about))
        conn.commit()
        hid = cursor.lastrowid
        conn.close()
        return hid

    @staticmethod
    def update(hospital_id, name, logo, banner, address, city, phone, email, departments, working_hours, emergency_contact, rating, total_beds, total_doctors, about):
        conn = get_db_connection()
        conn.execute('''
            UPDATE hospitals
            SET name=?, logo=?, banner=?, address=?, city=?, phone=?, email=?, departments=?, working_hours=?, emergency_contact=?, rating=?, total_beds=?, total_doctors=?, about=?
            WHERE id=?
        ''', (name, logo, banner, address, city, phone, email, departments, working_hours, emergency_contact, rating, total_beds, total_doctors, about, hospital_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(hospital_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM hospitals WHERE id = ?', (hospital_id,))
        conn.commit()
        conn.close()
