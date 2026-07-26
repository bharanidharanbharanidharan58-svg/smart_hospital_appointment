from flask import Blueprint, request, jsonify
from utils.ai_engine import AIEngine

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/analyze-symptoms', methods=['POST'])
def analyze_symptoms():
    data = request.get_json() or {}
    symptoms = data.get('symptoms', '').strip()
    if not symptoms:
        return jsonify({'error': 'Please enter or speak your symptoms.'}), 400
        
    result = AIEngine.analyze_symptoms(symptoms)
    return jsonify(result)

@ai_bp.route('/recommend-slot', methods=['POST'])
def recommend_slot():
    data = request.get_json() or {}
    doctor_id = data.get('doctor_id')
    preferred_time = data.get('preferred_time', 'morning')
    
    if not doctor_id:
        return jsonify({'error': 'Doctor ID is required'}), 400
        
    result = AIEngine.recommend_best_slot(doctor_id, preferred_time)
    return jsonify(result)

@ai_bp.route('/predict-queue', methods=['POST'])
def predict_queue():
    data = request.get_json() or {}
    queue_position = data.get('queue_position', 1)
    result = AIEngine.predict_queue(queue_position)
    return jsonify(result)

@ai_bp.route('/voice-assistant', methods=['POST'])
def voice_assistant():
    data = request.get_json() or {}
    command = data.get('command', '').strip()
    lang = data.get('lang', 'en')
    
    if not command:
        return jsonify({'response': 'I am listening. Please state your medical query or appointment request.'})
        
    result = AIEngine.process_voice_command(command, lang)
    return jsonify(result)
