import uuid
from datetime import datetime
from models.db import get_db_connection
from models.hospital import HospitalModel
from models.doctor import DoctorModel

class AppointmentModel:
    @staticmethod
    def is_slot_booked(doctor_id, appointment_date, time_slot):
        conn = get_db_connection()
        query = '''
            SELECT COUNT(*) as count FROM appointments
            WHERE doctor_id = ? AND appointment_date = ? AND time_slot = ?
            AND status IN ('Pending', 'Approved')
        '''
        res = conn.execute(query, (doctor_id, appointment_date, time_slot)).fetchone()
        conn.close()
        return res['count'] > 0

    @staticmethod
    def calculate_token_and_queue(doctor_id, hospital_id, department_id, appointment_date):
        conn = get_db_connection()
        
        # Get count of appointments for doctor on date
        seq_query = '''
            SELECT COUNT(*) as cnt FROM appointments
            WHERE doctor_id = ? AND appointment_date = ?
        '''
        seq_res = conn.execute(seq_query, (doctor_id, appointment_date)).fetchone()
        queue_pos = (seq_res['cnt'] or 0) + 1
        
        # Get codes
        doc = conn.execute('''
            SELECT d.id, h.code as h_code, dep.code as dep_code
            FROM doctors d
            JOIN hospitals h ON d.hospital_id = h.id
            JOIN departments dep ON d.department_id = dep.id
            WHERE d.id = ?
        ''', (doctor_id,)).fetchone()
        
        conn.close()
        
        h_code = doc['h_code'] if doc else 'HOSP'
        dep_code = doc['dep_code'] if doc else 'GEN'
        token_num = f"{h_code}-{dep_code}-{doctor_id:02d}-{queue_pos:03d}"
        predicted_wait = (queue_pos - 1) * 15 # 15 minutes per prior patient
        
        return token_num, queue_pos, predicted_wait

    @staticmethod
    def create(patient_id, doctor_id, hospital_id, department_id, appointment_date, time_slot, symptoms="", consultation_fee=500.0):
        # 1. Check double booking
        if AppointmentModel.is_slot_booked(doctor_id, appointment_date, time_slot):
            return None, "Error: This time slot is already booked for the selected doctor. Please select another slot."

        # 2. Token & Queue calculation
        token_num, queue_pos, predicted_wait = AppointmentModel.calculate_token_and_queue(
            doctor_id, hospital_id, department_id, appointment_date
        )
        
        appointment_number = "APT-" + uuid.uuid4().hex[:8].upper()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (
                appointment_number, patient_id, doctor_id, hospital_id, department_id,
                appointment_date, time_slot, status, token_number, queue_position,
                predicted_wait_time, symptoms, consultation_fee, payment_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Approved', ?, ?, ?, ?, ?, 'Paid')
        ''', (appointment_number, patient_id, doctor_id, hospital_id, department_id,
              appointment_date, time_slot, token_num, queue_pos, predicted_wait, symptoms, consultation_fee))
        
        conn.commit()
        apt_id = cursor.lastrowid
        conn.close()
        
        return apt_id, None

    @staticmethod
    def get_by_id(appointment_id):
        conn = get_db_connection()
        query = '''
            SELECT a.*,
                   p.name as patient_name, p.phone as patient_phone, p.email as patient_email, p.age as patient_age, p.gender as patient_gender, p.blood_group as patient_blood_group,
                   d.name as doctor_name, d.specialization as doctor_specialization, d.photo as doctor_photo, d.qualification as doctor_qualification,
                   h.name as hospital_name, h.address as hospital_address, h.phone as hospital_phone, h.email as hospital_email,
                   dep.name as department_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN departments dep ON a.department_id = dep.id
            WHERE a.id = ?
        '''
        apt = conn.execute(query, (appointment_id,)).fetchone()
        conn.close()
        return apt

    @staticmethod
    def get_by_patient(patient_id):
        conn = get_db_connection()
        query = '''
            SELECT a.*,
                   d.name as doctor_name, d.specialization as doctor_specialization, d.photo as doctor_photo,
                   h.name as hospital_name, dep.name as department_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN departments dep ON a.department_id = dep.id
            WHERE a.patient_id = ?
            ORDER BY a.appointment_date DESC, a.id DESC
        '''
        apts = conn.execute(query, (patient_id,)).fetchall()
        conn.close()
        return apts

    @staticmethod
    def get_by_doctor_today(doctor_id, date_str=None):
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        query = '''
            SELECT a.*,
                   p.name as patient_name, p.phone as patient_phone, p.age as patient_age, p.gender as patient_gender, p.blood_group as patient_blood_group, p.medical_history_summary,
                   dep.name as department_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN departments dep ON a.department_id = dep.id
            WHERE a.doctor_id = ? AND a.appointment_date = ?
            ORDER BY a.queue_position ASC
        '''
        apts = conn.execute(query, (doctor_id, date_str)).fetchall()
        conn.close()
        return apts

    @staticmethod
    def get_all_detailed():
        conn = get_db_connection()
        query = '''
            SELECT a.*,
                   p.name as patient_name,
                   d.name as doctor_name,
                   h.name as hospital_name,
                   dep.name as department_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN departments dep ON a.department_id = dep.id
            ORDER BY a.id DESC
        '''
        apts = conn.execute(query).fetchall()
        conn.close()
        return apts

    @staticmethod
    def update_status(appointment_id, status):
        conn = get_db_connection()
        conn.execute('UPDATE appointments SET status = ? WHERE id = ?', (status, appointment_id))
        conn.commit()
        conn.close()

    @staticmethod
    def reschedule(appointment_id, new_date, new_slot):
        apt = AppointmentModel.get_by_id(appointment_id)
        if not apt:
            return False, "Appointment not found."
        
        if AppointmentModel.is_slot_booked(apt['doctor_id'], new_date, new_slot):
            return False, "The selected new slot is already booked."

        conn = get_db_connection()
        conn.execute('''
            UPDATE appointments
            SET appointment_date = ?, time_slot = ?, status = 'Approved'
            WHERE id = ?
        ''', (new_date, new_slot, appointment_id))
        conn.commit()
        conn.close()
        return True, "Appointment rescheduled successfully."

    @staticmethod
    def cancel(appointment_id):
        conn = get_db_connection()
        conn.execute("UPDATE appointments SET status = 'Cancelled' WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        return True
