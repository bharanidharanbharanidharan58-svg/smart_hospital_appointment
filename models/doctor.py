from models.db import get_db_connection

class DoctorModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        query = '''
            SELECT d.*, h.name as hospital_name, dep.name as department_name, dep.code as department_code
            FROM doctors d
            JOIN hospitals h ON d.hospital_id = h.id
            JOIN departments dep ON d.department_id = dep.id
            ORDER BY d.id ASC
        '''
        doctors = conn.execute(query).fetchall()
        conn.close()
        return doctors

    @staticmethod
    def get_by_id(doctor_id):
        conn = get_db_connection()
        query = '''
            SELECT d.*, h.name as hospital_name, h.code as hospital_code, dep.name as department_name, dep.code as department_code
            FROM doctors d
            JOIN hospitals h ON d.hospital_id = h.id
            JOIN departments dep ON d.department_id = dep.id
            WHERE d.id = ?
        '''
        doctor = conn.execute(query, (doctor_id,)).fetchone()
        conn.close()
        return doctor

    @staticmethod
    def get_by_user_id(user_id):
        conn = get_db_connection()
        query = '''
            SELECT d.*, h.name as hospital_name, dep.name as department_name, dep.code as department_code
            FROM doctors d
            JOIN hospitals h ON d.hospital_id = h.id
            JOIN departments dep ON d.department_id = dep.id
            WHERE d.user_id = ?
        '''
        doctor = conn.execute(query, (user_id,)).fetchone()
        conn.close()
        return doctor

    @staticmethod
    def get_by_hospital(hospital_id):
        conn = get_db_connection()
        query = '''
            SELECT d.*, dep.name as department_name, dep.code as department_code
            FROM doctors d
            JOIN departments dep ON d.department_id = dep.id
            WHERE d.hospital_id = ?
            ORDER BY d.name ASC
        '''
        doctors = conn.execute(query, (hospital_id,)).fetchall()
        conn.close()
        return doctors

    @staticmethod
    def get_by_hospital_and_dept(hospital_id, department_id):
        conn = get_db_connection()
        query = '''
            SELECT d.*, dep.name as department_name, dep.code as department_code
            FROM doctors d
            JOIN departments dep ON d.department_id = dep.id
            WHERE d.hospital_id = ? AND d.department_id = ?
            ORDER BY d.name ASC
        '''
        doctors = conn.execute(query, (hospital_id, department_id,)).fetchall()
        conn.close()
        return doctors

    @staticmethod
    def filter_doctors(hospital_id=None, department_id=None, query_str=None):
        conn = get_db_connection()
        sql = '''
            SELECT d.*, h.name as hospital_name, dep.name as department_name
            FROM doctors d
            JOIN hospitals h ON d.hospital_id = h.id
            JOIN departments dep ON d.department_id = dep.id
            WHERE 1=1
        '''
        params = []
        if hospital_id:
            sql += ' AND d.hospital_id = ?'
            params.append(hospital_id)
        if department_id:
            sql += ' AND d.department_id = ?'
            params.append(department_id)
        if query_str:
            sql += ' AND (d.name LIKE ? OR d.specialization LIKE ? OR dep.name LIKE ?)'
            searchTerm = f'%{query_str}%'
            params.extend([searchTerm, searchTerm, searchTerm])
        
        sql += ' ORDER BY d.rating DESC'
        doctors = conn.execute(sql, params).fetchall()
        conn.close()
        return doctors

    @staticmethod
    def update_status(doctor_id, status):
        conn = get_db_connection()
        conn.execute('UPDATE doctors SET status = ? WHERE id = ?', (status, doctor_id))
        conn.commit()
        conn.close()

    @staticmethod
    def create(user_id, hospital_id, department_id, name, photo, qualification, experience, specialization, consultation_fee, working_days, available_time_slots, status='Online', languages='English', rating=4.9, about=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO doctors (user_id, hospital_id, department_id, name, photo, qualification, experience, specialization, consultation_fee, working_days, available_time_slots, status, languages, rating, about)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, hospital_id, department_id, name, photo, qualification, experience, specialization, consultation_fee, working_days, available_time_slots, status, languages, rating, about))
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        return doc_id

    @staticmethod
    def update(doctor_id, hospital_id, department_id, name, photo, qualification, experience, specialization, consultation_fee, working_days, available_time_slots, status, languages, rating, about):
        conn = get_db_connection()
        conn.execute('''
            UPDATE doctors
            SET hospital_id=?, department_id=?, name=?, photo=?, qualification=?, experience=?, specialization=?, consultation_fee=?, working_days=?, available_time_slots=?, status=?, languages=?, rating=?, about=?
            WHERE id=?
        ''', (hospital_id, department_id, name, photo, qualification, experience, specialization, consultation_fee, working_days, available_time_slots, status, languages, rating, about, doctor_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(doctor_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM doctors WHERE id = ?', (doctor_id,))
        conn.commit()
        conn.close()
