from flask import jsonify, abort, session, redirect, url_for
from db import SessionLocal, Subscription, User
from logger import setup_logger
from . import subscription_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

@subscription_bp.route('/<username>', methods=['DELETE'])
@admin_login_required
def delete_subscription(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.close()
        logger.warning(f"User {username} not found for subscription deletion")
        abort(404, description="User not found")
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not subscription:
        db.close()
        logger.warning(f"Subscription for user {username} not found for deletion")
        abort(404, description="Subscription not found")
    db.delete(subscription)
    db.commit()
    db.close()
    logger.info(f"Deleted subscription for user {username}")
    return jsonify({"message": "Subscription deleted"})
