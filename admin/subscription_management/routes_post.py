from flask import request, jsonify, abort
from db import SessionLocal, Subscription, User
from logger import setup_logger
from datetime import datetime
from . import subscription_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

@subscription_bp.route('/', methods=['POST'])
@admin_login_required
def create_subscription():
    data = request.json
    required_fields = ['username', 'plan', 'start_date', 'end_date', 'status']
    if not all(field in data for field in required_fields):
        logger.warning("Missing required subscription fields in create_subscription")
        abort(400, description="Missing required subscription fields")
    db = SessionLocal()
    user = db.query(User).filter(User.username == data['username']).first()
    if not user:
        db.close()
        logger.warning(f"User {data['username']} not found for subscription creation")
        abort(404, description="User not found")
    existing_sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if existing_sub:
        db.close()
        logger.warning(f"Subscription already exists for user {data['username']}")
        abort(400, description="Subscription already exists for user")
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
    except ValueError:
        db.close()
        logger.warning("Invalid date format in create_subscription")
        abort(400, description="Invalid date format, expected YYYY-MM-DD")
    new_sub = Subscription(
        user_id=user.id,
        plan=data['plan'],
        start_date=start_date,
        end_date=end_date,
        status=data['status']
    )
    db.add(new_sub)
    db.commit()
    db.close()
    logger.info(f"Created subscription for user {data['username']}")
    return jsonify({"message": "Subscription created"}), 201
