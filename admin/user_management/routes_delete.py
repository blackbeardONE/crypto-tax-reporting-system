from flask import jsonify, abort
from db import SessionLocal, User
from logger import setup_logger
from . import admin_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

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
