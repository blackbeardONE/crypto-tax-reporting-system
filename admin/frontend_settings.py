from flask import Blueprint, request, jsonify, abort, session, redirect, url_for
from admin.admin_auth import admin_login_required
from db import SessionLocal, FrontendSettings
from logger import setup_logger

frontend_settings_bp = Blueprint('frontend_settings', __name__, url_prefix='/admin/frontend-settings')

logger = setup_logger()

@frontend_settings_bp.before_request
def require_admin_login():
    if not session.get('username'):
        return redirect(url_for('admin_auth.login'))

@frontend_settings_bp.route('/', methods=['GET'])
@admin_login_required
def get_settings():
    db = SessionLocal()
    settings = db.query(FrontendSettings).first()
    db.close()
    if not settings:
        return jsonify({})
    return jsonify({
        'id': settings.id,
        'settings': settings.settings_json
    })

@frontend_settings_bp.route('/', methods=['POST'])
@admin_login_required
def update_settings():
    data = request.json
    if not data:
        abort(400, description="No settings data provided")
    db = SessionLocal()
    settings = db.query(FrontendSettings).first()
    if not settings:
        from models import FrontendSettings as FSModel
        settings = FSModel(settings_json=data)
        db.add(settings)
    else:
        settings.settings_json = data
    db.commit()
    db.close()
    logger.info("Frontend settings updated")
    return jsonify({"message": "Settings updated"})
