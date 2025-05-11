from flask import request, jsonify, abort
from db import SessionLocal, Subscription, User
from logger import setup_logger
from datetime import datetime
from . import subscription_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

@subscription_bp.route('/<username>', methods=['PUT'])
@admin_login_required
def update_subscription(username):
    data = request.json
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.close()
        logger.warning(f"User {username} not found for subscription update")
        abort(404, description="User not found")
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not subscription:
        db.close()
        logger.warning(f"Subscription for user {username} not found for update")
        abort(404, description="Subscription not found")
    for field in ['plan', 'start_date', 'end_date', 'status']:
        if field in data:
            if field in ['start_date', 'end_date']:
                try:
                    setattr(subscription, field, datetime.strptime(data[field], '%Y-%m-%d'))
                except ValueError:
                    db.close()
                    logger.warning(f"Invalid date format for {field} in update_subscription")
                    abort(400, description=f"Invalid date format for {field}, expected YYYY-MM-DD")
            else:
                setattr(subscription, field, data[field])
    db.commit()
    db.close()
    logger.info(f"Updated subscription for user {username}")
    return jsonify({"message": "Subscription updated"})
