from flask import request, jsonify, abort, session, redirect, url_for
from admin.admin_auth import admin_login_required
from db import SessionLocal, Subscription, User
from logger import setup_logger
from datetime import datetime
from . import subscription_bp

logger = setup_logger()

@subscription_bp.before_request
def require_admin_login():
    if not session.get('username'):
        return redirect(url_for('auth.login'))

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
