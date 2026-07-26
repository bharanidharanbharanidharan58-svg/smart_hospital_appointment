from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from utils.auth_helpers import admin_required
from models.hospital import HospitalModel
from models.doctor import DoctorModel
from models.patient import PatientModel
from models.appointment import AppointmentModel
from models.user import UserModel
from models.db import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    hospitals = HospitalModel.get_all()
    doctors = DoctorModel.get_all()
    patients = PatientModel.get_all()
    appointments = AppointmentModel.get_all_detailed()
    
    total_revenue = sum(a['consultation_fee'] for a in appointments if a['status'] in ('Approved', 'Completed'))
    
    # Analytics data by department
    conn = get_db_connection()
    dept_stats = conn.execute('''
        SELECT dep.name, COUNT(a.id) as total_appointments
        FROM departments dep
        LEFT JOIN appointments a ON dep.id = a.department_id
        GROUP BY dep.id
    ''').fetchall()
    conn.close()
    
    return render_template('admin/dashboard.html',
                           hospitals=hospitals,
                           doctors=doctors,
                           patients=patients,
                           appointments=appointments,
                           total_revenue=total_revenue,
                           dept_stats=dept_stats)

@admin_bp.route('/hospitals', methods=['GET', 'POST'])
@admin_required
def hospitals():
    if request.method == 'POST':
        action = request.form.get('action', 'create')
        if action == 'create':
            name = request.form.get('name')
            code = request.form.get('code')
            address = request.form.get('address')
            city = request.form.get('city')
            phone = request.form.get('phone')
            email = request.form.get('email')
            departments = request.form.get('departments')
            working_hours = request.form.get('working_hours', '24/7 Open')
            emergency_contact = request.form.get('emergency_contact')
            about = request.form.get('about', '')
            logo = request.form.get('logo', 'https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=120&q=80')
            banner = request.form.get('banner', 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80')
            
            HospitalModel.create(name, code, logo, banner, address, city, phone, email, departments, working_hours, emergency_contact, about=about)
            flash('New hospital branch registered successfully.', 'success')
            
        elif action == 'update':
            hid = request.form.get('hospital_id', type=int)
            name = request.form.get('name')
            address = request.form.get('address')
            city = request.form.get('city')
            phone = request.form.get('phone')
            email = request.form.get('email')
            departments = request.form.get('departments')
            working_hours = request.form.get('working_hours')
            emergency_contact = request.form.get('emergency_contact')
            rating = request.form.get('rating', 4.8, type=float)
            total_beds = request.form.get('total_beds', 250, type=int)
            total_doctors = request.form.get('total_doctors', 25, type=int)
            about = request.form.get('about', '')
            logo = request.form.get('logo')
            banner = request.form.get('banner')
            
            HospitalModel.update(hid, name, logo, banner, address, city, phone, email, departments, working_hours, emergency_contact, rating, total_beds, total_doctors, about)
            flash('Hospital details updated.', 'info')

        elif action == 'delete':
            hid = request.form.get('hospital_id', type=int)
            HospitalModel.delete(hid)
            flash('Hospital branch removed.', 'warning')

        return redirect(url_for('admin.hospitals'))

    hospitals_list = HospitalModel.get_all()
    return render_template('admin/hospitals.html', hospitals=hospitals_list)

@admin_bp.route('/doctors', methods=['GET', 'POST'])
@admin_required
def doctors():
    if request.method == 'POST':
        action = request.form.get('action', 'create')
        if action == 'create':
            name = request.form.get('name')
            email = request.form.get('email')
            hospital_id = request.form.get('hospital_id', type=int)
            department_id = request.form.get('department_id', type=int)
            qualification = request.form.get('qualification')
            experience = request.form.get('experience', 5, type=int)
            specialization = request.form.get('specialization')
            fee = request.form.get('consultation_fee', 500, type=float)
            working_days = request.form.get('working_days', 'Mon,Tue,Wed,Thu,Fri,Sat')
            time_slots = request.form.get('available_time_slots', '09:00 AM,09:30 AM,10:00 AM,10:30 AM,11:00 AM,04:00 PM,04:30 PM')
            languages = request.form.get('languages', 'English, Tamil')
            about = request.form.get('about', '')
            photo = request.form.get('photo', 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=300&q=80')
            
            # Create user for doctor
            user_id = UserModel.create_user(email, 'doctor123', 'doctor', name)
            DoctorModel.create(user_id, hospital_id, department_id, name, photo, qualification, experience, specialization, fee, working_days, time_slots, 'Online', languages, 4.9, about)
            flash('Doctor registered successfully.', 'success')

        elif action == 'delete':
            doc_id = request.form.get('doctor_id', type=int)
            DoctorModel.delete(doc_id)
            flash('Doctor profile deleted.', 'warning')

        return redirect(url_for('admin.doctors'))

    doctors_list = DoctorModel.get_all()
    hospitals_list = HospitalModel.get_all()
    conn = get_db_connection()
    departments_list = conn.execute('SELECT * FROM departments').fetchall()
    conn.close()
    return render_template('admin/doctors.html', doctors=doctors_list, hospitals=hospitals_list, departments=departments_list)

@admin_bp.route('/patients')
@admin_required
def patients():
    patients_list = PatientModel.get_all()
    return render_template('admin/patients.html', patients=patients_list)

@admin_bp.route('/appointments', methods=['GET', 'POST'])
@admin_required
def appointments():
    if request.method == 'POST':
        apt_id = request.form.get('appointment_id', type=int)
        status = request.form.get('status')
        AppointmentModel.update_status(apt_id, status)
        flash(f'Appointment #{apt_id} status changed to {status}.', 'success')
        return redirect(url_for('admin.appointments'))

    appointments_list = AppointmentModel.get_all_detailed()
    return render_template('admin/appointments.html', appointments=appointments_list)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    conn = get_db_connection()
    if request.method == 'POST':
        for key in request.form:
            val = request.form.get(key)
            conn.execute('INSERT OR REPLACE INTO system_settings (setting_key, setting_value) VALUES (?, ?)', (key, val))
        conn.commit()
        flash('System settings saved successfully.', 'success')
        
    settings_rows = conn.execute('SELECT * FROM system_settings').fetchall()
    conn.close()
    settings_dict = {r['setting_key']: r['setting_value'] for r in settings_rows}
    return render_template('admin/settings.html', settings=settings_dict)
