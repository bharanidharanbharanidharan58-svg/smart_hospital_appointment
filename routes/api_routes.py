from flask import Blueprint, jsonify, request
from models.hospital import HospitalModel
from models.doctor import DoctorModel
from models.appointment import AppointmentModel
from models.db import get_db_connection

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/hospitals')
def get_hospitals():
    hospitals = HospitalModel.get_all()
    return jsonify([dict(h) for h in hospitals])

@api_bp.route('/departments')
def get_departments():
    conn = get_db_connection()
    depts = conn.execute('SELECT * FROM departments ORDER BY name ASC').fetchall()
    conn.close()
    return jsonify([dict(d) for d in depts])

@api_bp.route('/doctors')
def get_doctors():
    hosp_id = request.args.get('hospital_id', type=int)
    dept_id = request.args.get('department_id', type=int)
    search_q = request.args.get('query', type=str)
    
    doctors = DoctorModel.filter_doctors(hospital_id=hosp_id, department_id=dept_id, query_str=search_q)
    return jsonify([dict(d) for d in doctors])

@api_bp.route('/doctor/<int:doctor_id>/slots')
def get_doctor_slots(doctor_id):
    date_str = request.args.get('date')
    doc = DoctorModel.get_by_id(doctor_id)
    if not doc:
        return jsonify({'error': 'Doctor not found'}), 404
        
    slots_list = [s.strip() for s in doc['available_time_slots'].split(',')]
    
    # Check booked status for each slot on date_str
    conn = get_db_connection()
    booked_slots = set()
    if date_str:
        rows = conn.execute('''
            SELECT time_slot FROM appointments
            WHERE doctor_id = ? AND appointment_date = ? AND status IN ('Pending', 'Approved')
        ''', (doctor_id, date_str)).fetchall()
        booked_slots = {r['time_slot'] for r in rows}
    conn.close()
    
    result_slots = []
    for slot in slots_list:
        result_slots.append({
            'slot': slot,
            'is_available': slot not in booked_slots
        })
        
    return jsonify({
        'doctor_id': doctor_id,
        'doctor_name': doc['name'],
        'consultation_fee': doc['consultation_fee'],
        'slots': result_slots
    })

@api_bp.route('/admin/analytics')
def admin_analytics():
    conn = get_db_connection()
    
    # 1. Revenue by Hospital
    revenue_by_hosp = conn.execute('''
        SELECT h.name, SUM(a.consultation_fee) as revenue
        FROM appointments a
        JOIN hospitals h ON a.hospital_id = h.id
        WHERE a.status IN ('Approved', 'Completed')
        GROUP BY h.id
        ORDER BY revenue DESC
    ''').fetchall()
    
    # 2. Appointments by Department
    dept_dist = conn.execute('''
        SELECT dep.name, COUNT(a.id) as count
        FROM appointments a
        JOIN departments dep ON a.department_id = dep.id
        GROUP BY dep.id
        ORDER BY count DESC
    ''').fetchall()

    # 3. Status Breakdown
    status_dist = conn.execute('''
        SELECT status, COUNT(id) as count
        FROM appointments
        GROUP BY status
    ''').fetchall()
    
    conn.close()

    return jsonify({
        'revenue_by_hospital': {
            'labels': [r['name'] for r in revenue_by_hosp],
            'data': [r['revenue'] for r in revenue_by_hosp]
        },
        'department_distribution': {
            'labels': [r['name'] for r in dept_dist],
            'data': [r['count'] for r in dept_dist]
        },
        'status_breakdown': {
            'labels': [r['status'] for r in status_dist],
            'data': [r['count'] for r in status_dist]
        }
    })
