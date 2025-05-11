from flask import Blueprint, jsonify, session, redirect, url_for
from admin.admin_auth import admin_login_required
from db import SessionLocal, Analytics
from logger import setup_logger

analytics_bp = Blueprint('analytics', __name__, url_prefix='/admin/analytics')

logger = setup_logger()

@analytics_bp.before_request
def require_admin_login():
    if not session.get('username'):
        return redirect(url_for('admin_auth.login'))

@analytics_bp.route('/', methods=['GET'])
@admin_login_required
def get_analytics():
    db = SessionLocal()
    analytics = db.query(Analytics).all()
    result = []
    for a in analytics:
        result.append({
            'id': a.id,
            'data': a.data_json
        })
    db.close()
    logger.info("Fetched analytics data")
    return jsonify(result)
