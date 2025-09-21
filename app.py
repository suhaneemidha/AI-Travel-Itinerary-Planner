# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from backend import VoiceAssistant
import os

app = Flask(__name__, static_folder='.')
CORS(app)

assistant = VoiceAssistant(headless=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_input = data.get('message')
    lang = data.get('lang', 'en')
    if not user_input:
        return jsonify({"reply": "No message received."})
    
    reply = assistant.process_command(user_input, lang)
    return jsonify({"reply": reply if reply else "Sorry, I couldn't process that."})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    num_people = data.get('numPeople')
    budget = data.get('budget')
    destination = data.get('destination')
    preferences = data.get('preferences', '')
    mode = data.get('mode', 'budget')
    refinement = data.get('refinement', '')
    lang = data.get('lang', 'en')

    if not all([start_date, end_date, destination]):
        return jsonify({"error": "Missing required fields"}), 400

    itinerary = assistant.generate_itinerary(
        start_date, end_date, num_people, budget, destination, preferences, mode, refinement, lang
    )

    if itinerary:
        return jsonify({"itinerary": itinerary})
    else:
        return jsonify({"error": "Failed to generate itinerary"}), 500

if __name__ == '__main__':
    app.run(debug=True)