import sqlite3
import os
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL, -- 'patient', 'doctor', 'admin'
            name TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Hospitals Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            logo TEXT,
            banner TEXT,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            departments TEXT NOT NULL, -- Comma separated department names
            working_hours TEXT NOT NULL,
            emergency_contact TEXT NOT NULL,
            rating REAL DEFAULT 4.8,
            total_beds INTEGER DEFAULT 250,
            total_doctors INTEGER DEFAULT 25,
            about TEXT
        )
    ''')

    # Departments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            icon TEXT
        )
    ''')

    # Doctors Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            hospital_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            photo TEXT,
            qualification TEXT NOT NULL,
            experience INTEGER NOT NULL, -- in years
            specialization TEXT NOT NULL,
            consultation_fee REAL NOT NULL,
            working_days TEXT NOT NULL, -- e.g. "Mon,Tue,Wed,Thu,Fri,Sat"
            available_time_slots TEXT NOT NULL, -- JSON or comma separated e.g. "09:00 AM,09:30 AM,10:00 AM"
            status TEXT DEFAULT 'Online', -- 'Online', 'Busy', 'On Leave'
            languages TEXT NOT NULL,
            rating REAL DEFAULT 4.9,
            about TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (hospital_id) REFERENCES hospitals (id),
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
    ''')

    # Patients Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            blood_group TEXT,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT,
            emergency_contact TEXT,
            medical_history_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Appointments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_number TEXT UNIQUE NOT NULL,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            hospital_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL, -- YYYY-MM-DD
            time_slot TEXT NOT NULL, -- HH:MM AM/PM
            status TEXT DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected', 'Completed', 'Cancelled'
            token_number TEXT NOT NULL,
            queue_position INTEGER DEFAULT 1,
            predicted_wait_time INTEGER DEFAULT 15, -- in minutes
            symptoms TEXT,
            consultation_fee REAL NOT NULL,
            payment_status TEXT DEFAULT 'Paid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id),
            FOREIGN KEY (hospital_id) REFERENCES hospitals (id),
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
    ''')

    # Medical Notes & Prescriptions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            diagnosis TEXT NOT NULL,
            prescription TEXT NOT NULL, -- Medicines with dosage
            lab_tests TEXT,
            follow_up_date TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments (id),
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
    ''')

    # System Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
