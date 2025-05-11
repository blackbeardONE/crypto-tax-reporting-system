from flask import request, jsonify, abort
from werkzeug.security import generate_password_hash
from db import SessionLocal, User
from logger import setup_logger
from . import admin_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

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
