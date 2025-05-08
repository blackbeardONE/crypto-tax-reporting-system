from flask import Blueprint, request, jsonify, abort, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from admin.admin_auth import admin_login_required
from db import SessionLocal, User
from logger import setup_logger

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

logger = setup_logger()

@admin_bp.before_request
def require_admin_login():
    if not session.get('admin_username'):
        return redirect(url_for('admin_auth.login'))

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

@admin_bp.route('/users', methods=['POST'])
@admin_login_required
def create_user():
    data = request.json
    required_fields = ['username', 'password', 'complete_name', 'company_name', 'company_address', 'company_email', 'company_phone']
    if not all(field in data for field in required_fields):
        logger.warning("Missing required user fields in create_user")
        abort(400, description="Missing required user fields")
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == data['username']).first()
    if existing_user:
        db.close()
        logger.warning(f"User {data['username']} already exists")
        abort(400, description="User already exists")
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        password_hash=hashed_password,
        complete_name=data['complete_name'],
        company_name=data['company_name'],
        company_address=data['company_address'],
        company_email=data['company_email'],
        company_phone=data['company_phone'],
        company_logo=data.get('company_logo')
    )
    db.add(new_user)
    db.commit()
    db.close()
    logger.info(f"Created new user {data['username']}")
    return jsonify({"message": "User created"}), 201

@admin_bp.route('/users/<username>', methods=['PUT'])
@admin_login_required
def update_user(username):
    data = request.json
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.close()
        logger.warning(f"User {username} not found for update")
        abort(404, description="User not found")
    for field in ['complete_name', 'company_name', 'company_address', 'company_email', 'company_phone', 'company_logo']:
        if field in data:
            setattr(user, field, data[field])
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
    db.commit()
    db.close()
    logger.info(f"Updated user {username}")
    return jsonify({"message": "User updated"})

@admin_bp.route('/users/<username>', methods=['DELETE'])
@admin_login_required
def delete_user(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.close()
        logger.warning(f"User {username} not found for deletion")
        abort(404, description="User not found")
    db.delete(user)
    db.commit()
    db.close()
    logger.info(f"Deleted user {username}")
    return jsonify({"message": "User deleted"})

@admin_bp.route('/users/manage')
@admin_login_required
def manage_users():
    return render_template('users.html')
