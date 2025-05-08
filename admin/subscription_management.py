from flask import Blueprint, request, jsonify, abort, session, redirect, url_for
from admin.admin_auth import admin_login_required
from db import SessionLocal, Subscription, User
from logger import setup_logger
from datetime import datetime

subscription_bp = Blueprint('subscription', __name__, url_prefix='/admin/subscription')

logger = setup_logger()

@subscription_bp.before_request
def require_admin_login():
    if not session.get('admin_username'):
        return redirect(url_for('admin_auth.login'))

@subscription_bp.route('/', methods=['GET'])
@admin_login_required
def get_subscriptions():
    db = SessionLocal()
    subscriptions = db.query(Subscription).all()
    result = []
    for sub in subscriptions:
        result.append({
            'id': sub.id,
            'username': sub.user.username if sub.user else None,
            'plan': sub.plan,
            'start_date': sub.start_date.strftime('%Y-%m-%d'),
            'end_date': sub.end_date.strftime('%Y-%m-%d'),
            'status': sub.status
        })
    db.close()
    logger.info("Fetched all subscriptions")
    return jsonify(result)

@subscription_bp.route('/<username>', methods=['GET'])
@admin_login_required
def get_subscription(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.close()
        logger.warning(f"User {username} not found for subscription fetch")
        abort(404, description="User not found")
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not subscription:
        db.close()
        logger.warning(f"Subscription for user {username} not found")
        abort(404, description="Subscription not found")
    result = {
        'id': subscription.id,
        'username': user.username,
        'plan': subscription.plan,
        'start_date': subscription.start_date.strftime('%Y-%m-%d'),
        'end_date': subscription.end_date.strftime('%Y-%m-%d'),
        'status': subscription.status
    }
    db.close()
    logger.info(f"Fetched subscription for user {username}")
    return jsonify(result)

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
