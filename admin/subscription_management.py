from flask import Blueprint, request, jsonify, abort, session, redirect, url_for
import os
import json
from admin.admin_auth import admin_login_required

subscription_bp = Blueprint('subscription', __name__, url_prefix='/admin/subscription')

SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), 'subscriptions.json')

def load_subscriptions():
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return {}
    with open(SUBSCRIPTIONS_FILE, 'r') as f:
        return json.load(f)

def save_subscriptions(subscriptions):
    with open(SUBSCRIPTIONS_FILE, 'w') as f:
        json.dump(subscriptions, f, indent=4)

@subscription_bp.before_request
def require_admin_login():
    if not session.get('admin_username'):
        return redirect(url_for('admin_auth.login'))

@subscription_bp.route('/', methods=['GET'])
@admin_login_required
def get_subscriptions():
    subscriptions = load_subscriptions()
    return jsonify(subscriptions)

@subscription_bp.route('/<username>', methods=['GET'])
@admin_login_required
def get_subscription(username):
    subscriptions = load_subscriptions()
    subscription = subscriptions.get(username)
    if not subscription:
        abort(404, description="Subscription not found")
    return jsonify(subscription)

@subscription_bp.route('/', methods=['POST'])
@admin_login_required
def create_subscription():
    data = request.json
    required_fields = ['username', 'plan', 'start_date', 'end_date', 'status']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required subscription fields")
    subscriptions = load_subscriptions()
    username = data['username']
    if username in subscriptions:
        abort(400, description="Subscription already exists for user")
    subscriptions[username] = {
        'plan': data['plan'],
        'start_date': data['start_date'],
        'end_date': data['end_date'],
        'status': data['status']
    }
    save_subscriptions(subscriptions)
    return jsonify({"message": "Subscription created"}), 201

@subscription_bp.route('/<username>', methods=['PUT'])
@admin_login_required
def update_subscription(username):
    data = request.json
    subscriptions = load_subscriptions()
    subscription = subscriptions.get(username)
    if not subscription:
        abort(404, description="Subscription not found")
    for field in ['plan', 'start_date', 'end_date', 'status']:
        if field in data:
            subscription[field] = data[field]
    subscriptions[username] = subscription
    save_subscriptions(subscriptions)
    return jsonify({"message": "Subscription updated"})

@subscription_bp.route('/<username>', methods=['DELETE'])
@admin_login_required
def delete_subscription(username):
    subscriptions = load_subscriptions()
    if username not in subscriptions:
        abort(404, description="Subscription not found")
    del subscriptions[username]
    save_subscriptions(subscriptions)
    return jsonify({"message": "Subscription deleted"})
