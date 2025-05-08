from flask import Blueprint, jsonify
import os
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/admin/analytics')

ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), 'analytics.json')

def load_analytics():
    if not os.path.exists(ANALYTICS_FILE):
        return {}
    with open(ANALYTICS_FILE, 'r') as f:
        return json.load(f)

@analytics_bp.route('/', methods=['GET'])
def get_analytics():
    analytics = load_analytics()
    return jsonify(analytics)
