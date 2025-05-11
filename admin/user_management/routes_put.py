from flask import request, jsonify, abort
from werkzeug.security import generate_password_hash
from db import SessionLocal, User
from logger import setup_logger
from . import admin_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

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
