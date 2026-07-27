from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from utils.auth_helpers import patient_required
from models.patient import PatientModel
from models.hospital import HospitalModel
from models.doctor import DoctorModel
from models.appointment import AppointmentModel
from models.medical_note import MedicalNoteModel
from utils.pdf_exporter import ReceiptExporter
from models.db import get_db_connection

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
@patient_required
def dashboard():
    patient_id = session.get('patient_id')
    patient = PatientModel.get_by_id(patient_id)
    appointments = AppointmentModel.get_by_patient(patient_id)
    hospitals = HospitalModel.get_all()
    doctors = DoctorModel.get_all()
    
    upcoming = [a for a in appointments if a['status'] in ('Pending', 'Approved')]
    past = [a for a in appointments if a['status'] in ('Completed', 'Cancelled', 'Rejected')]
    
    return render_template(
    'patient/dashboard.html',
    patient=patient,
    user_name=patient['name'],
    appointments=appointments,
    upcoming_count=len(upcoming),
    completed_count=len([a for a in appointments if a['status'] == 'Completed']),
    hospitals=hospitals
)

@patient_bp.route('/book', methods=['GET', 'POST'])
@patient_required
def book_appointment():
    patient_id = session.get('patient_id')
    patient = PatientModel.get_by_id(patient_id)
    
    if request.method == 'POST':
        hospital_id = request.form.get('hospital_id', type=int)
        department_id = request.form.get('department_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        appointment_date = request.form.get('appointment_date')
        time_slot = request.form.get('time_slot')
        symptoms = request.form.get('symptoms', '').strip()
        
        doc = DoctorModel.get_by_id(doctor_id)
        fee = doc['consultation_fee'] if doc else 500.0

        apt_id, error = AppointmentModel.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            department_id=department_id,
            appointment_date=appointment_date,
            time_slot=time_slot,
            symptoms=symptoms,
            consultation_fee=fee
        )

        if error:
            flash(error, 'danger')
            return redirect(url_for('patient.book_appointment', hospital_id=hospital_id, department_id=department_id))

        flash('Appointment booked successfully! Smart token generated.', 'success')
        return redirect(url_for('patient.view_receipt', appointment_id=apt_id))

    # GET Request: Prepare dropdown options
    selected_hosp = request.args.get('hospital_id', type=int)
    selected_dept = request.args.get('department_id', type=int)
    
    hospitals = HospitalModel.get_all()
    
    conn = get_db_connection()
    departments = conn.execute('SELECT * FROM departments ORDER BY name ASC').fetchall()
    conn.close()
    
    doctors = []
    if selected_hosp:
        if selected_dept:
            doctors = DoctorModel.get_by_hospital_and_dept(selected_hosp, selected_dept)
        else:
            doctors = DoctorModel.get_by_hospital(selected_hosp)

    return render_template('patient/book_appointment.html',
                           patient=patient,
                           hospitals=hospitals,
                           departments=departments,
                           doctors=doctors,
                           selected_hosp=selected_hosp,
                           selected_dept=selected_dept)

@patient_bp.route('/receipt/<int:appointment_id>')
@patient_required
def view_receipt(appointment_id):
    apt = AppointmentModel.get_by_id(appointment_id)
    if not apt or apt['patient_id'] != session.get('patient_id'):
        flash('Appointment record not found.', 'danger')
        return redirect(url_for('patient.dashboard'))
        
    medical_note = MedicalNoteModel.get_by_appointment(appointment_id)
    return render_template('patient/receipt.html', appointment=apt, medical_note=medical_note)

@patient_bp.route('/receipt/<int:appointment_id>/print')
@patient_required
def print_receipt(appointment_id):
    apt = AppointmentModel.get_by_id(appointment_id)
    if not apt or apt['patient_id'] != session.get('patient_id'):
        return "Access denied or record missing", 403
        
    medical_note = MedicalNoteModel.get_by_appointment(appointment_id)
    html_content = ReceiptExporter.generate_receipt_html(apt, medical_note)
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@patient_bp.route('/cancel/<int:appointment_id>', methods=['POST'])
@patient_required
def cancel_appointment(appointment_id):
    apt = AppointmentModel.get_by_id(appointment_id)
    if apt and apt['patient_id'] == session.get('patient_id'):
        AppointmentModel.cancel(appointment_id)
        flash('Appointment cancelled.', 'info')
    else:
        flash('Unable to cancel appointment.', 'danger')
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/history')
@patient_required
def history():
    patient_id = session.get('patient_id')
    patient = PatientModel.get_by_id(patient_id)
    notes = MedicalNoteModel.get_by_patient(patient_id)
    appointments = AppointmentModel.get_by_patient(patient_id)
    return render_template('patient/history.html', patient=patient, notes=notes, appointments=appointments)

@patient_bp.route('/ai-symptom-checker')
@patient_required
def ai_symptom():
    return render_template('patient/ai_symptom.html')
