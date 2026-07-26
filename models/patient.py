from models.db import get_db_connection

class PatientModel:
    @staticmethod
    def create(user_id, name, age, gender, blood_group, phone, email, address="", emergency_contact="", medical_history_summary=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patients (user_id, name, age, gender, blood_group, phone, email, address, emergency_contact, medical_history_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, age, gender, blood_group, phone, email, address, emergency_contact, medical_history_summary))
        conn.commit()
        pid = cursor.lastrowid
        conn.close()
        return pid

    @staticmethod
    def get_by_user_id(user_id):
        conn = get_db_connection()
        patient = conn.execute('SELECT * FROM patients WHERE user_id = ?', (user_id,)).fetchone()
        conn.close()
        return patient

    @staticmethod
    def get_by_id(patient_id):
        conn = get_db_connection()
        patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
        conn.close()
        return patient

    @staticmethod
    def get_all():
        conn = get_db_connection()
        patients = conn.execute('SELECT * FROM patients ORDER BY id DESC').fetchall()
        conn.close()
        return patients

    @staticmethod
    def update(patient_id, name, age, gender, blood_group, phone, email, address, emergency_contact, medical_history_summary):
        conn = get_db_connection()
        conn.execute('''
            UPDATE patients
            SET name=?, age=?, gender=?, blood_group=?, phone=?, email=?, address=?, emergency_contact=?, medical_history_summary=?
            WHERE id=?
        ''', (name, age, gender, blood_group, phone, email, address, emergency_contact, medical_history_summary, patient_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(patient_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
        conn.commit()
        conn.close()
