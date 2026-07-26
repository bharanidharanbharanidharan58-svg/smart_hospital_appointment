import re
from models.doctor import DoctorModel
from models.hospital import HospitalModel
from models.db import get_db_connection

class AIEngine:
    SYMPTOM_MAP = {
        'Cardiology': ['chest pain', 'heart', 'palpitations', 'shortness of breath', 'high blood pressure', 'cardiac', 'நெஞ்சு வலி', 'இதயம்'],
        'Neurology': ['headache', 'migraine', 'dizziness', 'seizure', 'numbness', 'memory loss', 'paralysis', 'தலைவலி', 'மயக்கம்'],
        'Orthopedics': ['joint pain', 'fracture', 'knee pain', 'back pain', 'bone', 'arthritis', 'muscle sprain', 'மூட்டு வலி', 'எலும்பு'],
        'Dermatology': ['skin rash', 'acne', 'itching', 'eczema', 'psoriasis', 'hair loss', 'skin allergy', 'தோல் நோய்', 'அரிப்பு'],
        'Gastroenterology': ['stomach pain', 'indigestion', 'acidity', 'nausea', 'vomiting', 'diarrhea', 'ulcer', 'வயிறு வலி'],
        'Ophthalmology': ['eye pain', 'blurry vision', 'cataract', 'redness in eye', 'sight issue', 'கண் வலி', 'பார்வை'],
        'ENT': ['ear pain', 'throat pain', 'cough', 'sinus', 'tonsils', 'hearing issue', 'காது வலி', 'தொண்டை வலி', 'இருமல்'],
        'Pediatrics': ['child fever', 'pediatric', 'infant cough', 'child growth', 'குழந்தை காய்ச்சல்'],
        'Oncology': ['lump', 'unexplained weight loss', 'tumour', 'cancer consultation', 'புற்றுநோய்'],
        'General Medicine': ['fever', 'cold', 'body pain', 'fatigue', 'weakness', 'flu', 'காய்ச்சல்', 'சளி', 'உடல் வலி']
    }

    @staticmethod
    def analyze_symptoms(symptoms_text):
        symptoms_text = symptoms_text.lower()
        dept_scores = {}
        
        for dept, keywords in AIEngine.SYMPTOM_MAP.items():
            score = sum(1 for kw in keywords if kw in symptoms_text)
            if score > 0:
                dept_scores[dept] = score
                
        if not dept_scores:
            matched_dept = 'General Medicine'
            confidence = 65.0
        else:
            matched_dept = max(dept_scores, key=dept_scores.get)
            confidence = min(95.0, 70.0 + (dept_scores[matched_dept] * 10.0))
            
        # Get matching department details from DB
        conn = get_db_connection()
        dept_row = conn.execute('SELECT * FROM departments WHERE name = ?', (matched_dept,)).fetchone()
        conn.close()
        
        department_id = dept_row['id'] if dept_row else 1
        
        # Get recommended doctors for this department
        recommended_doctors = DoctorModel.filter_doctors(department_id=department_id)
        
        # Prepare recommendation response
        return {
            'analyzed_symptoms': symptoms_text,
            'recommended_department': matched_dept,
            'department_id': department_id,
            'confidence': confidence,
            'advice': f"Based on your reported symptoms, we strongly recommend consulting a specialist in {matched_dept}.",
            'doctors': [dict(doc) for doc in recommended_doctors[:4]]
        }

    @staticmethod
    def recommend_best_slot(doctor_id, preferred_time="morning"):
        doc = DoctorModel.get_by_id(doctor_id)
        if not doc:
            return None
            
        all_slots = [s.strip() for s in doc['available_time_slots'].split(',')]
        
        if preferred_time.lower() == "morning":
            matching = [s for s in all_slots if "AM" in s]
        elif preferred_time.lower() == "afternoon":
            matching = [s for s in all_slots if "12:" in s or "01:" in s or "02:" in s or "03:" in s]
        else:
            matching = [s for s in all_slots if "04:" in s or "05:" in s or "06:" in s or "07:" in s or "PM" in s]
            
        best_slot = matching[0] if matching else all_slots[0]
        return {
            'recommended_slot': best_slot,
            'available_slots': all_slots,
            'reasoning': f"AI evaluated Doctor availability and picked the optimal {preferred_time} consultation window."
        }

    @staticmethod
    def predict_queue(queue_position):
        wait_time = max(0, (queue_position - 1) * 15)
        status = "On Schedule" if wait_time < 30 else "Moderate Delay"
        return {
            'queue_position': queue_position,
            'predicted_wait_minutes': wait_time,
            'status': status,
            'ai_tip': " Arrive 10 minutes prior to your estimated slot to complete pre-checkin."
        }

    @staticmethod
    def process_voice_command(text, lang='en'):
        text = text.strip()
        text_lower = text.lower()
        
        # Check if Tamil or English query
        is_tamil = any('\u0b80' <= c <= '\u0bff' for c in text) or lang.startswith('ta')
        
        if "book" in text_lower or "appointment" in text_lower or "முன்பதிவு" in text:
            response_en = "Opening appointment booking wizard. You can select your preferred hospital and doctor."
            response_ta = "மருத்துவமனை முன்பதிவு பக்கத்தை திறக்கிறேன். உங்கள் மருத்துவமனையை தேர்ந்தெடுக்கலாம்."
            return {
                'action': 'navigate',
                'target': '/patient/book',
                'response': response_ta if is_tamil else response_en
            }
        elif "symptom" in text_lower or "fever" in text_lower or "pain" in text_lower or "நோய்" in text or "காய்ச்சல்" in text:
            symptom_res = AIEngine.analyze_symptoms(text)
            dept = symptom_res['recommended_department']
            response_en = f"I evaluated your symptoms. You should consult a {dept} specialist."
            response_ta = f"உங்கள் அறிகுறிகளின் அடிப்படையில் {dept} மருத்துவரை அணுக பரிந்துரைக்கிறோம்."
            return {
                'action': 'symptom_analysis',
                'result': symptom_res,
                'response': response_ta if is_tamil else response_en
            }
        elif "hospital" in text_lower or "apollo" in text_lower or "kauvery" in text_lower or "மருத்துவமனை" in text:
            hospitals = HospitalModel.get_all()
            response_en = f"Aura Health is connected with {len(hospitals)} premier hospital networks across Tamil Nadu & India."
            response_ta = f"ஆரா ஹெல்த் {len(hospitals)} முன்னணி மருத்துவமனைகளுடன் இணைந்து செயல்படுகிறது."
            return {
                'action': 'info',
                'response': response_ta if is_tamil else response_en,
                'data': [dict(h) for h in hospitals[:5]]
            }
        else:
            response_en = f"Hello! I am Aura AI Voice Assistant. How can I assist with your healthcare today?"
            response_ta = f"வணக்கம்! நான் ஆரா AI குரல் உதவியாளர். உங்களுக்கு எப்படி உதவட்டும்?"
            return {
                'action': 'chat',
                'response': response_ta if is_tamil else response_en
            }
