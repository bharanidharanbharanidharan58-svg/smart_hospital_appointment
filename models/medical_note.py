from models.db import get_db_connection

class MedicalNoteModel:
    @staticmethod
    def create(appointment_id, patient_id, doctor_id, diagnosis, prescription, lab_tests="", follow_up_date="", notes=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medical_notes (appointment_id, patient_id, doctor_id, diagnosis, prescription, lab_tests, follow_up_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (appointment_id, patient_id, doctor_id, diagnosis, prescription, lab_tests, follow_up_date, notes))
        conn.commit()
        note_id = cursor.lastrowid
        
        # Mark appointment as Completed
        cursor.execute("UPDATE appointments SET status = 'Completed' WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        return note_id

    @staticmethod
    def get_by_patient(patient_id):
        conn = get_db_connection()
        query = '''
            SELECT mn.*,
                   d.name as doctor_name, d.specialization as doctor_specialization,
                   h.name as hospital_name,
                   a.appointment_number, a.appointment_date, a.time_slot
            FROM medical_notes mn
            JOIN doctors d ON mn.doctor_id = d.id
            JOIN appointments a ON mn.appointment_id = a.id
            JOIN hospitals h ON a.hospital_id = h.id
            WHERE mn.patient_id = ?
            ORDER BY mn.created_at DESC
        '''
        notes = conn.execute(query, (patient_id,)).fetchall()
        conn.close()
        return notes

    @staticmethod
    def get_by_appointment(appointment_id):
        conn = get_db_connection()
        query = '''
            SELECT mn.*, d.name as doctor_name, d.specialization as doctor_specialization
            FROM medical_notes mn
            JOIN doctors d ON mn.doctor_id = d.id
            WHERE mn.appointment_id = ?
        '''
        note = conn.execute(query, (appointment_id,)).fetchone()
        conn.close()
        return note
