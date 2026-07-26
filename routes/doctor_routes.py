from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth_helpers import doctor_required
from models.doctor import DoctorModel
from models.appointment import AppointmentModel
from models.medical_note import MedicalNoteModel
from models.patient import PatientModel
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    doctor_id = session.get('doctor_id')
    doctor = DoctorModel.get_by_id(doctor_id)
    today_str = datetime.now().strftime('%Y-%m-%d')
    queue = AppointmentModel.get_by_doctor_today(doctor_id, today_str)
    
    pending_count = len([a for a in queue if a['status'] in ('Pending', 'Approved')])
    completed_count = len([a for a in queue if a['status'] == 'Completed'])
    
    return render_template('doctor/dashboard.html',
                           doctor=doctor,
                           queue=queue,
                           today_date=today_str,
                           pending_count=pending_count,
                           completed_count=completed_count)

@doctor_bp.route('/status', methods=['POST'])
@doctor_required
def update_status():
    doctor_id = session.get('doctor_id')
    status = request.form.get('status', 'Online')
    DoctorModel.update_status(doctor_id, status)
    flash(f'Status updated to {status}.', 'success')
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/consultation/<int:appointment_id>', methods=['GET', 'POST'])
@doctor_required
def consultation(appointment_id):
    doctor_id = session.get('doctor_id')
    doctor = DoctorModel.get_by_id(doctor_id)
    appointment = AppointmentModel.get_by_id(appointment_id)
    
    if not appointment or appointment['doctor_id'] != doctor_id:
        flash('Appointment record not accessible.', 'danger')
        return redirect(url_for('doctor.dashboard'))
        
    patient = PatientModel.get_by_id(appointment['patient_id'])
    patient_history = MedicalNoteModel.get_by_patient(appointment['patient_id'])
    existing_note = MedicalNoteModel.get_by_appointment(appointment_id)
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis', '').strip()
        prescription = request.form.get('prescription', '').strip()
        lab_tests = request.form.get('lab_tests', '').strip()
        follow_up_date = request.form.get('follow_up_date', '').strip()
        notes = request.form.get('notes', '').strip()
        
        MedicalNoteModel.create(
            appointment_id=appointment_id,
            patient_id=appointment['patient_id'],
            doctor_id=doctor_id,
            diagnosis=diagnosis,
            prescription=prescription,
            lab_tests=lab_tests,
            follow_up_date=follow_up_date,
            notes=notes
        )
        flash('Medical consultation completed & prescription issued.', 'success')
        return redirect(url_for('doctor.dashboard'))
        
    return render_template('doctor/patient_detail.html',
                           doctor=doctor,
                           appointment=appointment,
                           patient=patient,
                           patient_history=patient_history,
                           existing_note=existing_note)

@doctor_bp.route('/appointment/<int:appointment_id>/action', methods=['POST'])
@doctor_required
def update_appointment_action(appointment_id):
    action = request.form.get('action') # 'approve', 'reject', 'complete'
    doctor_id = session.get('doctor_id')
    apt = AppointmentModel.get_by_id(appointment_id)
    
    if apt and apt['doctor_id'] == doctor_id:
        if action == 'approve':
            AppointmentModel.update_status(appointment_id, 'Approved')
            flash('Appointment Approved.', 'success')
        elif action == 'reject':
            AppointmentModel.update_status(appointment_id, 'Rejected')
            flash('Appointment Rejected.', 'warning')
        elif action == 'complete':
            AppointmentModel.update_status(appointment_id, 'Completed')
            flash('Appointment marked as Completed.', 'info')
            
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/profile')
@doctor_required
def profile():
    doctor_id = session.get('doctor_id')
    doctor = DoctorModel.get_by_id(doctor_id)
    return render_template('doctor/profile.html', doctor=doctor)
