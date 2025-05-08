from flask import Blueprint, request, jsonify, abort
import os
import json

frontend_settings_bp = Blueprint('frontend_settings', __name__, url_prefix='/admin/frontend-settings')

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'frontend_settings.json')

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

@frontend_settings_bp.route('/', methods=['GET'])
def get_settings():
    settings = load_settings()
    return jsonify(settings)

@frontend_settings_bp.route('/', methods=['POST'])
def update_settings():
    data = request.json
    if not data:
        abort(400, description="No settings data provided")
    save_settings(data)
    return jsonify({"message": "Settings updated"})
