from flask import jsonify, abort, session, redirect, url_for, render_template
from db import SessionLocal, User
from logger import setup_logger
from . import admin_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

@admin_bp.before_request
def require_admin_login():
    if not session.get('username'):
        return redirect(url_for('auth.login'))

@admin_bp.route('/users', methods=['GET'])
@admin_login_required
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    users_safe = []
    for user in users:
        users_safe.append({
            'username': user.username,
            'complete_name': user.complete_name,
            'company_name': user.company_name,
            'company_address': user.company_address,
            'company_email': user.company_email,
            'company_phone': user.company_phone,
            'company_logo': user.company_logo
        })
    db.close()
    logger.info("Fetched all users")
    return jsonify(users_safe)

@admin_bp.route('/users/<username>', methods=['GET'])
@admin_login_required
def get_user(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.close()
        logger.warning(f"User {username} not found")
        abort(404, description="User not found")
    user_safe = {
        'username': user.username,
        'complete_name': user.complete_name,
        'company_name': user.company_name,
        'company_address': user.company_address,
        'company_email': user.company_email,
        'company_phone': user.company_phone,
        'company_logo': user.company_logo
    }
    db.close()
    logger.info(f"Fetched user {username}")
    return jsonify(user_safe)

@admin_bp.route('/users/manage')
@admin_login_required
def manage_users():
    return render_template('users.html')
