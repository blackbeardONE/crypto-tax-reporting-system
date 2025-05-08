from flask import Blueprint, request, jsonify, abort
import os
import json
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/admin/reports')

REPORTS_FILE = os.path.join(os.path.dirname(__file__), 'reports.json')

def load_reports():
    if not os.path.exists(REPORTS_FILE):
        return {}
    with open(REPORTS_FILE, 'r') as f:
        return json.load(f)

def save_reports(reports):
    with open(REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=4)

@reports_bp.route('/', methods=['GET'])
def get_reports():
    reports = load_reports()
    return jsonify(reports)

@reports_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id):
    reports = load_reports()
    report = reports.get(report_id)
    if not report:
        abort(404, description="Report not found")
    return jsonify(report)

@reports_bp.route('/', methods=['POST'])
def create_report():
    data = request.json
    required_fields = ['id', 'user_id', 'generated_at', 'file_path']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required report fields")
    reports = load_reports()
    report_id = data['id']
    if report_id in reports:
        abort(400, description="Report ID already exists")
    reports[report_id] = {
        'user_id': data['user_id'],
        'generated_at': data['generated_at'],
        'file_path': data['file_path']
    }
    save_reports(reports)
    return jsonify({"message": "Report created"}), 201

@reports_bp.route('/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    reports = load_reports()
    if report_id not in reports:
        abort(404, description="Report not found")
    del reports[report_id]
    save_reports(reports)
    return jsonify({"message": "Report deleted"})
