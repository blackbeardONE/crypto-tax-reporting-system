from flask import Blueprint, request, jsonify, abort, session, redirect, url_for
from admin.admin_auth import admin_login_required
from db import SessionLocal, Report
from logger import setup_logger
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/admin/reports')

logger = setup_logger()

@reports_bp.before_request
def require_admin_login():
    if not session.get('username'):
        return redirect(url_for('admin_auth.login'))

@reports_bp.route('/', methods=['GET'])
@admin_login_required
def get_reports():
    db = SessionLocal()
    reports = db.query(Report).all()
    result = []
    for rep in reports:
        result.append({
            'id': rep.id,
            'user_id': rep.user_id,
            'generated_at': rep.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'file_path': rep.file_path
        })
    db.close()
    logger.info("Fetched all reports")
    return jsonify(result)

@reports_bp.route('/<int:report_id>', methods=['GET'])
@admin_login_required
def get_report(report_id):
    db = SessionLocal()
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        db.close()
        logger.warning(f"Report {report_id} not found")
        abort(404, description="Report not found")
    result = {
        'id': report.id,
        'user_id': report.user_id,
        'generated_at': report.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'file_path': report.file_path
    }
    db.close()
    logger.info(f"Fetched report {report_id}")
    return jsonify(result)

@reports_bp.route('/', methods=['POST'])
@admin_login_required
def create_report():
    data = request.json
    required_fields = ['user_id', 'generated_at', 'file_path']
    if not all(field in data for field in required_fields):
        logger.warning("Missing required report fields in create_report")
        abort(400, description="Missing required report fields")
    db = SessionLocal()
    try:
        generated_at = datetime.strptime(data['generated_at'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        db.close()
        logger.warning("Invalid datetime format in create_report")
        abort(400, description="Invalid datetime format, expected YYYY-MM-DD HH:MM:SS")
    new_report = Report(
        user_id=data['user_id'],
        generated_at=generated_at,
        file_path=data['file_path']
    )
    db.add(new_report)
    db.commit()
    db.close()
    logger.info(f"Created report for user {data['user_id']}")
    return jsonify({"message": "Report created"}), 201

@reports_bp.route('/<int:report_id>', methods=['DELETE'])
@admin_login_required
def delete_report(report_id):
    db = SessionLocal()
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        db.close()
        logger.warning(f"Report {report_id} not found for deletion")
        abort(404, description="Report not found")
    db.delete(report)
    db.commit()
    db.close()
    logger.info(f"Deleted report {report_id}")
    return jsonify({"message": "Report deleted"})
