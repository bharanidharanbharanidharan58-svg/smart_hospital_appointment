from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import UserModel
from models.patient import PatientModel
from models.doctor import DoctorModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        selected_role = request.form.get('role', 'patient')

        user = UserModel.get_by_email(email)
        if not user or not UserModel.verify_password(user['password_hash'], password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', selected_role=selected_role, email=email)

        if user['role'] != selected_role and user['role'] != 'admin':
            flash(f'Account role mismatch. This user is registered as {user["role"].capitalize()}.', 'warning')
            return render_template('auth/login.html', selected_role=selected_role, email=email)

        # Set Session
        session.clear()
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['name'] = user['name']
        session['role'] = user['role']

        if user['role'] == 'patient':
            patient = PatientModel.get_by_user_id(user['id'])
            if patient:
                session['patient_id'] = patient['id']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('patient.dashboard'))

        elif user['role'] == 'doctor':
            doctor = DoctorModel.get_by_user_id(user['id'])
            if doctor:
                session['doctor_id'] = doctor['id']
            flash(f'Welcome Dr. {user["name"]}!', 'success')
            return redirect(url_for('doctor.dashboard'))

        elif user['role'] == 'admin':
            flash('Welcome Administrator!', 'success')
            return redirect(url_for('admin.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        age = request.form.get('age', 30, type=int)
        gender = request.form.get('gender', 'Male')
        blood_group = request.form.get('blood_group', 'O+')
        address = request.form.get('address', '').strip()

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if UserModel.get_by_email(email):
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register.html')

        user_id = UserModel.create_user(email, password, 'patient', name, phone)
        if user_id:
            patient_id = PatientModel.create(user_id, name, age, gender, blood_group, phone, email, address)
            
            # Auto login
            session.clear()
            session['user_id'] = user_id
            session['email'] = email
            session['name'] = name
            session['role'] = 'patient'
            session['patient_id'] = patient_id
            
            flash('Registration successful! Welcome to Aura Health.', 'success')
            return redirect(url_for('patient.dashboard'))
        else:
            flash('Failed to create account. Please try again.', 'danger')

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))
