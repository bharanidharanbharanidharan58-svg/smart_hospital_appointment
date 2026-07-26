import sqlite3
from config import Config
from models.db import init_db, get_db_connection
from werkzeug.security import generate_password_hash

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already seeded
    existing_hospitals = cursor.execute('SELECT COUNT(*) as cnt FROM hospitals').fetchone()['cnt']
    if existing_hospitals >= 10:
        print("Database already seeded with 10 hospitals!")
        conn.close()
        return

    print("Seeding database with enterprise hospital & doctor data...")

    # 1. System Settings
    settings = [
        ('system_name', 'Aura Health Enterprise'),
        ('emergency_helpline', '108 / 1800-425-AURA'),
        ('currency', 'INR (₹)'),
        ('ai_symptom_checker', 'Enabled'),
        ('voice_assistant', 'Enabled'),
        ('teleconsultation', 'Active')
    ]
    for key, val in settings:
        cursor.execute('INSERT OR REPLACE INTO system_settings (setting_key, setting_value) VALUES (?, ?)', (key, val))

    # 2. Departments
    departments_data = [
        ('Cardiology', 'CARD', 'Heart & Cardiovascular Care', 'fa-heartbeat'),
        ('Neurology', 'NEUR', 'Brain, Spine & Nerve Disorders', 'fa-brain'),
        ('Orthopedics', 'ORTH', 'Bone, Joint & Spine Surgery', 'fa-bone'),
        ('Dermatology', 'DERM', 'Skin, Hair & Cosmetic Treatments', 'fa-allergies'),
        ('Gastroenterology', 'GAST', 'Digestive System & Liver Diseases', 'fa-stethoscope'),
        ('Ophthalmology', 'OPHT', 'Advanced Eye Care & Surgery', 'fa-eye'),
        ('ENT', 'ENT', 'Ear, Nose, Throat & Head Surgery', 'fa-deaf'),
        ('Pediatrics', 'PEDI', 'Child Health & Newborn Care', 'fa-baby'),
        ('Oncology', 'ONCO', 'Comprehensive Cancer Care & Therapy', 'fa-ribbon'),
        ('General Medicine', 'GENM', 'General Diagnosis & Preventive Care', 'fa-user-md')
    ]
    cursor.executemany('INSERT OR IGNORE INTO departments (name, code, description, icon) VALUES (?, ?, ?, ?)', departments_data)
    conn.commit()

    # Get department IDs
    dept_rows = cursor.execute('SELECT id, name FROM departments').fetchall()
    dept_map = {row['name']: row['id'] for row in dept_rows}

    # 3. Users (Admin, Doctor accounts, Patient accounts)
    admin_hash = generate_password_hash('admin123')
    doctor_hash = generate_password_hash('doctor123')
    patient_hash = generate_password_hash('patient123')

    cursor.execute('INSERT OR IGNORE INTO users (email, password_hash, role, name, phone) VALUES (?, ?, ?, ?, ?)',
                   ('admin@aurahealth.com', admin_hash, 'admin', 'System Administrator', '+91 9876543210'))

    # 4. Hospitals (10 Real Hospitals)
    hospitals = [
        {
            'name': 'Apollo Hospital', 'code': 'APO',
            'logo': 'https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80',
            'address': 'Greams Lane, 21 Greams Rd, Thousand Lights, Chennai, Tamil Nadu 600006',
            'city': 'Chennai', 'phone': '+91 44 2829 0200', 'email': 'info@apollohospitals.com',
            'departments': 'Cardiology, Neurology, Orthopedics, Oncology, Gastroenterology, General Medicine',
            'working_hours': '24/7 Open', 'emergency_contact': '1066 / +91 44 2829 3333',
            'rating': 4.9, 'total_beds': 600, 'total_doctors': 120,
            'about': 'Apollo Hospitals Chennai is India’s first corporate hospital and a global healthcare pioneer with world-class organ transplant and cardiology units.'
        },
        {
            'name': 'Kauvery Hospital', 'code': 'KAU',
            'logo': 'https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=1200&q=80',
            'address': 'No. 1, KC Road, Tennur, Tiruchirappalli, Tamil Nadu 620017',
            'city': 'Trichy', 'phone': '+91 431 4077 777', 'email': 'care@kauveryhospital.com',
            'departments': 'Cardiology, Orthopedics, ENT, Pediatrics, General Medicine, Gastroenterology',
            'working_hours': '24/7 Open', 'emergency_contact': '+91 431 4077 000',
            'rating': 4.8, 'total_beds': 450, 'total_doctors': 85,
            'about': 'Kauvery Hospital is a premier multi-specialty tertiary care hospital chain dedicated to patient-centric treatment and advanced diagnostics.'
        },
        {
            'name': 'KMCH Hospital', 'code': 'KMCH',
            'logo': 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1200&q=80',
            'address': 'Avinashi Road, Civil Aerodrome Post, Coimbatore, Tamil Nadu 641014',
            'city': 'Coimbatore', 'phone': '+91 422 4323 800', 'email': 'info@kmchhospitals.com',
            'departments': 'Neurology, Cardiology, Orthopedics, Ophthalmology, Dermatology, ENT',
            'working_hours': '24/7 Open', 'emergency_contact': '+91 422 4323 999',
            'rating': 4.9, 'total_beds': 750, 'total_doctors': 150,
            'about': 'Kovai Medical Center and Hospital (KMCH) is Western Tamil Nadu’s most trusted super-specialty hospital with robotic surgery and trauma care.'
        },
        {
            'name': 'PSG Hospitals', 'code': 'PSG',
            'logo': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1512678080530-7760d81faba6?auto=format&fit=crop&w=1200&q=80',
            'address': 'Peelamedu, Avinashi Road, Coimbatore, Tamil Nadu 641004',
            'city': 'Coimbatore', 'phone': '+91 422 2570 170', 'email': 'contact@psghospitals.com',
            'departments': 'Pediatrics, Oncology, General Medicine, Gastroenterology, Dermatology',
            'working_hours': '24/7 Open', 'emergency_contact': '+91 422 2570 108',
            'rating': 4.7, 'total_beds': 800, 'total_doctors': 140,
            'about': 'PSG Hospitals provides comprehensive multi-disciplinary clinical care, teaching excellence, and advanced research facilities.'
        },
        {
            'name': 'Sri Ramakrishna Hospital', 'code': 'SRH',
            'logo': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80',
            'address': '395, Sarojini Naidu Rd, Sidhapudur, Coimbatore, Tamil Nadu 641044',
            'city': 'Coimbatore', 'phone': '+91 422 4500 000', 'email': 'help@sriramakrishnahospital.com',
            'departments': 'Cardiology, Oncology, Orthopedics, Ophthalmology, ENT',
            'working_hours': '24/7 Open', 'emergency_contact': '+91 422 4500 108',
            'rating': 4.8, 'total_beds': 550, 'total_doctors': 90,
            'about': 'Sri Ramakrishna Hospital is famed for pioneering affordable cancer care, open-heart surgery, and neurosurgery.'
        },
        {
            'name': 'Ganga Hospital', 'code': 'GNG',
            'logo': 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=1200&q=80',
            'address': 313, 'address': '313, Mettupalayam Rd, Saibaba Colony, Coimbatore, Tamil Nadu 641043',
            'city': 'Coimbatore', 'phone': '+91 422 2485 000', 'email': 'info@gangahospital.com',
            'departments': 'Orthopedics, Neurology, General Medicine, Dermatology',
            'working_hours': '24/7 Open', 'emergency_contact': '+91 422 2485 108',
            'rating': 4.95, 'total_beds': 650, 'total_doctors': 95,
            'about': 'Ganga Hospital is internationally renowned for Orthopedics, Trauma, Spine Surgery, and Reconstructive Microsurgery.'
        },
        {
            'name': 'Royal Care Hospital', 'code': 'RCH',
            'logo': 'https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=1200&q=80',
            'address': '1/520, L&T Bypass Road, Neelambur, Coimbatore, Tamil Nadu 641062',
            'city': 'Coimbatore', 'phone': '+91 422 2227 000', 'email': 'info@royalcarehospital.in',
            'departments': 'Cardiology, Gastroenterology, Neurology, Oncology, Pediatrics',
            'working_hours': '24/7 Open', 'emergency_contact': '+91 422 2227 108',
            'rating': 4.85, 'total_beds': 500, 'total_doctors': 80,
            'about': 'Royal Care Super Specialty Hospital delivers international standards in critical care, stroke care, and interventional radiology.'
        },
        {
            'name': 'GEM Hospital', 'code': 'GEM',
            'logo': 'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1512678080530-7760d81faba6?auto=format&fit=crop&w=1200&q=80',
            'address': '45, Pankaja Mill Rd, Ramanathapuram, Coimbatore, Tamil Nadu 641045',
            'city': 'Coimbatore', 'phone': '+91 422 2325 100', 'email': 'gem@gemhospital.org',
            'departments': 'Gastroenterology, Oncology, General Medicine, Dermatology',
            'working_hours': '24/7 Open', 'emergency_contact': '+91 422 2325 108',
            'rating': 4.9, 'total_beds': 350, 'total_doctors': 60,
            'about': 'GEM Hospital is Asia’s premier institute for Gastroenterology and Laparoscopic/Robotic surgery.'
        },
        {
            'name': 'Kauvery Hospital Chennai', 'code': 'KAC',
            'logo': 'https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80',
            'address': '199, Luz Church Rd, Mylapore, Chennai, Tamil Nadu 600004',
            'city': 'Chennai', 'phone': '+91 44 4000 6000', 'email': 'chennai@kauveryhospital.com',
            'departments': 'Cardiology, Neurology, Pediatrics, Orthopedics, ENT, Ophthalmology',
            'working_hours': '24/7 Open', 'emergency_contact': '+91 44 4000 6108',
            'rating': 4.88, 'total_beds': 400, 'total_doctors': 90,
            'about': 'Kauvery Hospital Chennai Mylapore delivers high-end tertiary healthcare across heart care, neuroscience, and geriatric medicine.'
        },
        {
            'name': 'AIIMS Delhi', 'code': 'AIM',
            'logo': 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=120&q=80',
            'banner': 'https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1200&q=80',
            'address': 'Sri Aurobindo Marg, Ansari Nagar, New Delhi, Delhi 110029',
            'city': 'New Delhi', 'phone': '+91 11 2658 8500', 'email': 'contact@aiims.edu',
            'departments': 'Cardiology, Neurology, Orthopedics, Oncology, Pediatrics, ENT, Ophthalmology, Dermatology',
            'working_hours': '24/7 Open', 'emergency_contact': '102 / +91 11 2658 8700',
            'rating': 4.98, 'total_beds': 2500, 'total_doctors': 450,
            'about': 'All India Institute of Medical Sciences (AIIMS) Delhi is India’s apex public medical institution and premier research hospital.'
        }
    ]

    for h in hospitals:
        cursor.execute('''
            INSERT INTO hospitals (name, code, logo, banner, address, city, phone, email, departments, working_hours, emergency_contact, rating, total_beds, total_doctors, about)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (h['name'], h['code'], h['logo'], h['banner'], h['address'], h['city'], h['phone'], h['email'], h['departments'], h['working_hours'], h['emergency_contact'], h['rating'], h['total_beds'], h['total_doctors'], h['about']))
    conn.commit()

    # Get Hospital map
    hosp_rows = cursor.execute('SELECT id, name FROM hospitals').fetchall()
    hosp_map = {r['name']: r['id'] for r in hosp_rows}

    # 5. Create 40+ Doctors
    # We will generate 4+ doctors for each hospital across departments
    doctors_raw = [
        # Apollo Hospital (Hosp ID: Apollo Hospital)
        ("Apollo Hospital", "Cardiology", "Dr. K. Saminathan", "MD, DM (Cardiology), FACC", 22, "Senior Interventional Cardiologist", 1200, "Mon,Tue,Wed,Thu,Fri,Sat", "09:00 AM,09:30 AM,10:00 AM,10:30 AM,11:00 AM,04:00 PM,04:30 PM", "Online", "English, Tamil", 4.9, "Expert in coronary angioplasty, TAVI procedures, and heart failure management with over 20 years of clinical mastery."),
        ("Apollo Hospital", "Neurology", "Dr. Meenakshi Sundaram", "DM (Neurology), FINR", 18, "Chief Neurosurgeon & Stroke Specialist", 1100, "Mon,Wed,Fri,Sat", "10:00 AM,10:30 AM,11:00 AM,02:00 PM,02:30 PM", "Online", "English, Tamil, Hindi", 4.8, "Renowned expert in endoscopic spine surgery, epilepsy management, and brain tumor resections."),
        ("Apollo Hospital", "Orthopedics", "Dr. Vijay C. Bose", "MS (Ortho), FRCS (Glasgow)", 25, "Joint Replacement Specialist", 1300, "Tue,Thu,Sat", "09:00 AM,10:00 AM,11:30 AM,03:00 PM,04:00 PM", "Online", "English, Tamil", 4.95, "World pioneer in hip resurfacing and complex revision knee joint surgeries."),
        ("Apollo Hospital", "Oncology", "Dr. Preetha Reddy", "MD (Onco), DNB", 16, "Medical Oncologist", 1000, "Mon,Tue,Wed,Fri", "09:30 AM,11:00 AM,02:00 PM,03:30 PM", "Online", "English, Tamil, Telugu", 4.85, "Specialist in targeted immunotherapy and breast cancer therapeutic protocols."),

        # Kauvery Hospital (Trichy)
        ("Kauvery Hospital", "Cardiology", "Dr. T. Senthil Kumar", "MD, DM (Cardiology)", 17, "Chief Cardiologist", 800, "Mon,Tue,Wed,Thu,Fri,Sat", "09:00 AM,10:00 AM,11:00 AM,05:00 PM,06:00 PM", "Online", "English, Tamil", 4.85, "Specializes in radial angioplasty, pacemaker implantations, and pediatric echo diagnosis."),
        ("Kauvery Hospital", "Orthopedics", "Dr. A. Velmurugan", "MS (Ortho), D.Ortho", 15, "Trauma & Orthopedic Surgeon", 750, "Mon,Wed,Fri,Sat", "09:30 AM,10:30 AM,03:00 PM,04:00 PM", "Online", "English, Tamil", 4.75, "Experienced in arthroscopic knee repairs, sports injuries, and pelvic fractures."),
        ("Kauvery Hospital", "ENT", "Dr. S. Deepa", "MS (ENT), DLO", 12, "ENT & Head Neck Surgeon", 650, "Mon,Tue,Thu,Fri,Sat", "10:00 AM,11:00 AM,12:00 PM,04:00 PM", "Online", "English, Tamil", 4.7, "Specialist in sinus endoscopic surgery, hearing restoration, and micro-ear procedures."),
        ("Kauvery Hospital", "Pediatrics", "Dr. R. Rajesh", "MD (Pediatrics), DCH", 14, "Senior Pediatrician & Neonatologist", 700, "Mon,Tue,Wed,Thu,Fri,Sat", "09:00 AM,11:00 AM,04:00 PM,06:00 PM", "Online", "English, Tamil", 4.9, "Focused on newborn intensive care, immunization, and childhood developmental disorders."),

        # KMCH Hospital
        ("KMCH Hospital", "Neurology", "Dr. V. Arulselvan", "MD, DM (Neurology)", 20, "Director of Neuro Sciences", 1000, "Mon,Tue,Wed,Thu,Fri", "09:00 AM,10:00 AM,11:30 AM,02:30 PM", "Online", "English, Tamil", 4.9, "Leading specialist in Parkinson’s care, stroke rehabilitation, and nerve conduction diagnostics."),
        ("KMCH Hospital", "Cardiology", "Dr. Thomas Alexander", "MD, DM, FACC", 24, "Chief Interventional Cardiologist", 1100, "Mon,Wed,Fri,Sat", "10:00 AM,11:00 AM,12:00 PM,03:30 PM", "Online", "English, Tamil, Malayalam", 4.92, "Pioneer of rural STEMI heart attack intervention programs across South India."),
        ("KMCH Hospital", "Ophthalmology", "Dr. S. Natarajan", "MS (Ophth), FRCS", 19, "Vitreoretinal Surgeon", 850, "Tue,Thu,Sat", "09:00 AM,10:30 AM,02:00 PM,04:00 PM", "Online", "English, Tamil", 4.8, "Expert in laser cataract surgery, retinal detachment repair, and diabetic retinopathy."),
        ("KMCH Hospital", "Dermatology", "Dr. Radhika Krishnan", "MD (Derm), DNB", 11, "Cosmetic Dermatologist", 700, "Mon,Tue,Thu,Fri", "10:00 AM,11:30 AM,04:00 PM,05:30 PM", "Online", "English, Tamil", 4.75, "Specialist in laser skin resurfacing, acne scar removal, and clinical dermatology."),

        # PSG Hospitals
        ("PSG Hospitals", "Pediatrics", "Dr. J. Balasubramaniam", "MD (Pedi), DCH", 21, "Head of Pediatrics", 800, "Mon,Tue,Wed,Thu,Fri,Sat", "09:00 AM,10:00 AM,11:00 AM,03:00 PM", "Online", "English, Tamil", 4.88, "Senior expert in pediatric asthma, childhood infections, and adolescent medicine."),
        ("PSG Hospitals", "Oncology", "Dr. M. S. Guhan", "MD, DM (Medical Oncology)", 16, "Senior Oncologist", 950, "Mon,Wed,Fri", "10:00 AM,11:30 AM,02:00 PM,03:30 PM", "Online", "English, Tamil", 4.82, "Integrates precision chemotherapy and targeted molecular oncotherapy."),
        ("PSG Hospitals", "Gastroenterology", "Dr. K. Srinivas", "MD, DM (Gastro)", 15, "Gastroenterologist & Hepatologist", 850, "Mon,Tue,Thu,Fri,Sat", "09:30 AM,11:00 AM,04:00 PM,05:00 PM", "Online", "English, Tamil", 4.8, "Specialist in ERCP, endoscopy, fatty liver disease, and inflammatory bowel syndrome."),
        ("PSG Hospitals", "General Medicine", "Dr. P. V. Ramachandran", "MD (Gen Med)", 23, "Senior Consultant Physician", 700, "Mon,Tue,Wed,Thu,Fri,Sat", "08:30 AM,10:00 AM,04:30 PM,06:00 PM", "Online", "English, Tamil", 4.9, "Master clinician in diabetic care, hypertension management, and complex multi-system fever."),

        # Sri Ramakrishna Hospital
        ("Sri Ramakrishna Hospital", "Cardiology", "Dr. S. Manoharan", "MD, DM (Cardiology)", 20, "Consultant Interventional Cardiologist", 900, "Mon,Tue,Thu,Fri,Sat", "09:00 AM,10:30 AM,02:00 PM,04:00 PM", "Online", "English, Tamil", 4.86, "Expert in keyhole valve replacement, balloon angioplasty, and cardiac intensive care."),
        ("Sri Ramakrishna Hospital", "Oncology", "Dr. P. Guhan", "MS, MCh (Surgical Oncology)", 22, "Director of Sri Ramakrishna Oncology Centre", 1000, "Mon,Wed,Fri,Sat", "10:00 AM,11:30 AM,03:00 PM,05:00 PM", "Online", "English, Tamil", 4.93, "Renowned surgical oncologist specializing in head, neck, and gastrointestinal cancers."),
        ("Sri Ramakrishna Hospital", "ENT", "Dr. R. M. Shenoy", "MS (ENT)", 14, "Senior ENT Consultant", 600, "Mon,Tue,Wed,Fri,Sat", "09:30 AM,11:00 AM,04:00 PM,05:30 PM", "Online", "English, Tamil", 4.7, "Specialist in vertigo treatment, snoring surgery, and micro-laryngeal operations."),
        ("Sri Ramakrishna Hospital", "Ophthalmology", "Dr. N. Anand", "DO, DNB (Ophth)", 13, "Cornea & Refractive Specialist", 650, "Tue,Thu,Sat", "09:00 AM,10:30 AM,02:30 PM,04:00 PM", "Online", "English, Tamil", 4.75, "Specialist in LASIK vision correction, keratoconus, and corneal transplantation."),

        # Ganga Hospital
        ("Ganga Hospital", "Orthopedics", "Dr. S. Rajasekaran", "MS (Ortho), FRCS, PhD", 30, "Chairman & Chief Spine Surgeon", 1500, "Mon,Wed,Fri", "09:00 AM,11:00 AM,02:00 PM,04:00 PM", "Online", "English, Tamil", 4.99, "World authority in spine deformity correction, disc replacement, and trauma research."),
        ("Ganga Hospital", "Orthopedics", "Dr. Raja Sabapathy", "MS, MCh (Plastic), FRCS", 28, "Chief Hand & Microsurgeon", 1400, "Tue,Thu,Sat", "09:30 AM,11:30 AM,03:00 PM,05:00 PM", "Online", "English, Tamil", 4.98, "Global icon in limb re-plantation, brachial plexus surgery, and reconstructive plastic surgery."),
        ("Ganga Hospital", "Neurology", "Dr. K. Sundararajan", "DM (Neurology)", 16, "Consultant Neurologist", 900, "Mon,Tue,Thu,Fri,Sat", "10:00 AM,11:30 AM,04:00 PM,05:30 PM", "Online", "English, Tamil", 4.8, "Specializes in neuro-muscular disorders, spine pain management, and EEG diagnostics."),
        ("Ganga Hospital", "Dermatology", "Dr. Sheila Stephen", "MD (Dermatology)", 12, "Dermatologist & Cosmetologist", 700, "Mon,Wed,Fri", "10:00 AM,12:00 PM,03:30 PM,05:00 PM", "Online", "English, Tamil", 4.78, "Focuses on skin trauma recovery, scar revision, and pediatric skin conditions."),

        # Royal Care Hospital
        ("Royal Care Hospital", "Cardiology", "Dr. K. M. Cherian", "MS, MCh (Cardio-Thoracic)", 26, "Chief Cardiac Surgeon", 1200, "Mon,Tue,Wed,Thu,Fri", "09:00 AM,10:30 AM,02:00 PM,03:30 PM", "Online", "English, Tamil", 4.94, "Legendary cardiac surgeon specializing in bypass grafts and valve reconstructions."),
        ("Royal Care Hospital", "Gastroenterology", "Dr. Parameswaran", "MD, DM (Gastro)", 18, "Chief Gastroenterologist", 950, "Mon,Wed,Fri,Sat", "09:30 AM,11:00 AM,04:00 PM,05:30 PM", "Online", "English, Tamil", 4.85, "Specialist in therapeutic endoscopy, pancreatic disorders, and liver transplant care."),
        ("Royal Care Hospital", "Pediatrics", "Dr. Sunitha Menon", "MD (Pedi), Fellowship in Neonatology", 13, "Senior Pediatric Consultant", 750, "Mon,Tue,Thu,Fri,Sat", "10:00 AM,11:30 AM,03:00 PM,04:30 PM", "Online", "English, Tamil, Malayalam", 4.82, "Expert in child nutrition, pediatric infections, and newborn care."),
        ("Royal Care Hospital", "Neurology", "Dr. A. R. Vasanth", "DM (Neuro)", 15, "Consultant Neuro-Physician", 900, "Tue,Thu,Sat", "09:00 AM,10:30 AM,02:30 PM,04:00 PM", "Online", "English, Tamil", 4.79, "Focuses on stroke thrombolysis, epilepsy, and autonomic nervous disorders."),

        # GEM Hospital
        ("GEM Hospital", "Gastroenterology", "Dr. C. Palanivelu", "MS, MCh, FRCS, FACS", 32, "Chairman & Pioneer Laparoscopic Surgeon", 1500, "Mon,Wed,Fri", "09:30 AM,11:30 AM,03:00 PM,04:30 PM", "Online", "English, Tamil", 4.99, "Pioneered keyhole laparoscopic cancer surgery in India with international acclaim."),
        ("GEM Hospital", "Gastroenterology", "Dr. P. Senthilnathan", "MS, Fellowship in Bariatric Surgery", 19, "Chief Bariatric & GI Surgeon", 1100, "Mon,Tue,Thu,Fri,Sat", "10:00 AM,11:30 AM,04:00 PM,06:00 PM", "Online", "English, Tamil", 4.9, "Specialist in weight loss bariatric surgery, hernia repair, and GI oncology."),
        ("GEM Hospital", "Oncology", "Dr. Swaminathan", "MD (Onco)", 14, "GI Medical Oncologist", 900, "Mon,Wed,Fri,Sat", "09:00 AM,10:30 AM,02:00 PM,03:30 PM", "Online", "English, Tamil", 4.8, "Focuses on digestive tract cancers, chemo-embolization, and palliative oncology care."),
        ("GEM Hospital", "General Medicine", "Dr. N. Karthik", "MD (Gen Med)", 11, "General Physician & Diabetologist", 650, "Mon,Tue,Wed,Thu,Fri,Sat", "08:30 AM,10:00 AM,04:00 PM,05:30 PM", "Online", "English, Tamil", 4.75, "Specializes in diabetes lifestyle management, metabolic syndrome, and general illness."),

        # Kauvery Hospital Chennai (Mylapore)
        ("Kauvery Hospital Chennai", "Cardiology", "Dr. A. B. Gopalamurugan", "MD, DM, FRCP (London)", 20, "Senior Interventional Cardiologist", 1200, "Mon,Tue,Wed,Thu,Fri,Sat", "09:00 AM,10:30 AM,01:30 PM,03:00 PM", "Online", "English, Tamil", 4.91, "Pioneer in TAVI, structural heart interventions, and complex coronary stenting."),
        ("Kauvery Hospital Chennai", "Neurology", "Dr. S. Sitaraman", "DM (Neurology)", 17, "Senior Neuro Physician", 1000, "Mon,Wed,Fri,Sat", "10:00 AM,11:30 AM,03:30 PM,05:00 PM", "Online", "English, Tamil", 4.85, "Expert in headache clinic, neuromuscular weakness, and cognitive neurology."),
        ("Kauvery Hospital Chennai", "ENT", "Dr. A. S. Prashanth", "MS (ENT), DLO", 13, "Head & Neck ENT Specialist", 750, "Mon,Tue,Thu,Fri,Sat", "09:30 AM,11:00 AM,04:00 PM,05:30 PM", "Online", "English, Tamil", 4.78, "Focuses on endoscopic ear surgery, allergy clinic, and voice disorders."),
        ("Kauvery Hospital Chennai", "Pediatrics", "Dr. Lakshmi Prabha", "MD (Pediatrics)", 14, "Pediatrician & Child Specialist", 750, "Mon,Tue,Wed,Thu,Fri,Sat", "09:00 AM,10:30 AM,04:00 PM,06:00 PM", "Online", "English, Tamil", 4.84, "Specializes in pediatric growth monitoring, immunizations, and respiratory care."),

        # AIIMS Delhi
        ("AIIMS Delhi", "Cardiology", "Dr. Randeep Guleria", "MD, DM (Pulmonary & Cardio-Vascular)", 30, "Senior Director & Clinical Master", 1500, "Mon,Wed,Fri", "09:00 AM,10:30 AM,02:00 PM,04:00 PM", "Online", "English, Hindi", 4.99, "Renowned national medical authority and leader in cardio-respiratory medicine."),
        ("AIIMS Delhi", "Neurology", "Dr. M. V. Padma Srivastava", "MD, DM (Neurology), FAMS", 26, "Head of Neurosciences AIIMS", 1400, "Mon,Tue,Thu,Fri", "09:30 AM,11:00 AM,02:30 PM,04:00 PM", "Online", "English, Hindi", 4.97, "National pioneer in acute stroke management, neuro-rehabilitation, and brain research."),
        ("AIIMS Delhi", "Orthopedics", "Dr. Rajesh Malhotra", "MS (Ortho), FRCS", 28, "Chief of Trauma Centre & Ortho", 1450, "Tue,Thu,Sat", "09:00 AM,11:00 AM,03:00 PM,05:00 PM", "Online", "English, Hindi", 4.96, "Specialist in complex trauma revision, joint replacement, and orthopedic oncology."),
        ("AIIMS Delhi", "Oncology", "Dr. G. K. Rath", "MD (Radiation Oncology)", 29, "Director National Cancer Institute", 1400, "Mon,Wed,Fri,Sat", "10:00 AM,11:30 AM,02:00 PM,03:30 PM", "Online", "English, Hindi", 4.95, "Pioneer in proton beam therapy, precision radiation, and clinical trial cancer research."),
        ("AIIMS Delhi", "Dermatology", "Dr. Vinod K. Sharma", "MD (Derm), FAMS", 22, "Chief Dermatologist AIIMS", 1000, "Mon,Tue,Wed,Fri", "09:30 AM,11:00 AM,03:30 PM,05:00 PM", "Online", "English, Hindi", 4.88, "Specialist in autoimmune skin diseases, vitiligo surgery, and psoriasis biology."),
        ("AIIMS Delhi", "Gastroenterology", "Dr. Pramod Garg", "MD, DM (Gastro)", 24, "Professor & Head Gastroenterology", 1200, "Mon,Wed,Fri", "09:00 AM,10:30 AM,02:00 PM,04:00 PM", "Online", "English, Hindi", 4.92, "World-renowned researcher in acute pancreatitis, liver failure, and GI endoscopy.")
    ]

    doctor_photos = [
        "https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=300&q=80",
        "https://images.unsplash.com/photo-1594824813571-2153349a65e6?auto=format&fit=crop&w=300&q=80",
        "https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&w=300&q=80",
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=300&q=80",
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=300&q=80",
        "https://images.unsplash.com/photo-1582750433449-648ed127bb54?auto=format&fit=crop&w=300&q=80"
    ]

    idx = 0
    for hosp_name, dept_name, doc_name, qual, exp, spec, fee, days, slots, status, langs, rating, about in doctors_raw:
        if hosp_name not in hosp_map or dept_name not in dept_map:
            continue
            
        h_id = hosp_map[hosp_name]
        d_id = dept_map[dept_name]
        photo = doctor_photos[idx % len(doctor_photos)]
        idx += 1
        
        # Create user account for doctor
        doc_email = f"doctor.{idx}@aurahealth.com"
        cursor.execute('INSERT OR IGNORE INTO users (email, password_hash, role, name, phone) VALUES (?, ?, ?, ?, ?)',
                       (doc_email, doctor_hash, 'doctor', doc_name, '+91 9876500' + str(100 + idx)))
        user_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO doctors (user_id, hospital_id, department_id, name, photo, qualification, experience, specialization, consultation_fee, working_days, available_time_slots, status, languages, rating, about)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, h_id, d_id, doc_name, photo, qual, exp, spec, fee, days, slots, status, langs, rating, about))

    conn.commit()

    # 6. Seed Demo Patients & Appointments
    patient_user_id = cursor.execute('INSERT INTO users (email, password_hash, role, name, phone) VALUES (?, ?, ?, ?, ?)',
                                     ('patient@aurahealth.com', patient_hash, 'patient', 'Rajesh Kumar', '+91 9123456789')).lastrowid

    cursor.execute('''
        INSERT INTO patients (user_id, name, age, gender, blood_group, phone, email, address, emergency_contact, medical_history_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (patient_user_id, 'Rajesh Kumar', 34, 'Male', 'O+ Pos', '+91 9123456789', 'patient@aurahealth.com', '124 Anna Salai, Chennai', '+91 9876543210', 'Mild hypertension, No known drug allergies'))
    patient_id = cursor.lastrowid

    # Create Sample Appointments
    sample_apts = [
        ('APT-8F92A1B0', patient_id, 1, 1, 1, '2026-07-27', '09:30 AM', 'Approved', 'APO-CARD-01-001', 1, 0, 'Chest discomfort during morning exercise', 1200.0),
        ('APT-3C14D8E9', patient_id, 5, 2, 1, '2026-07-28', '10:00 AM', 'Approved', 'KAU-CARD-05-001', 1, 0, 'Routine cardiac health review', 800.0),
        ('APT-7E20F5A4', patient_id, 9, 3, 2, '2026-07-20', '11:30 AM', 'Completed', 'KMCH-NEUR-09-003', 3, 30, 'Recurrent migraine and fatigue', 1000.0)
    ]

    for apt in sample_apts:
        cursor.execute('''
            INSERT INTO appointments (appointment_number, patient_id, doctor_id, hospital_id, department_id, appointment_date, time_slot, status, token_number, queue_position, predicted_wait_time, symptoms, consultation_fee, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Paid')
        ''', apt)
        apt_id = cursor.lastrowid
        
        # Add sample medical note for completed appointment
        if apt[7] == 'Completed':
            cursor.execute('''
                INSERT INTO medical_notes (appointment_id, patient_id, doctor_id, diagnosis, prescription, lab_tests, follow_up_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (apt_id, patient_id, 9, 'Stress Migraine & Cervical Muscle Tension', '1. Tab Naprosyn 500mg - 1-0-1 after food (5 days)\n2. Tab Neurobion Forte - 0-1-0 (30 days)\n3. Cervical posture exercise daily', 'MRI Brain Screening', '2026-08-20', 'Patient advised to maintain hydration and regular sleep cycles.'))

    conn.commit()
    conn.close()
    print("Database successfully seeded with 10 hospitals, 40+ doctors, demo patients & appointments!")

if __name__ == '__main__':
    seed_database()
