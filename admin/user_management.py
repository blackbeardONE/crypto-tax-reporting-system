from flask import Blueprint, request, jsonify, abort, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from admin.admin_auth import admin_login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@admin_bp.before_request
def require_admin_login():
    if not session.get('admin_username'):
        return redirect(url_for('admin_auth.login'))

@admin_bp.route('/users', methods=['GET'])
@admin_login_required
def get_users():
    users = load_users()
    # Do not expose passwords
    users_safe = {u: {k: v for k, v in data.items() if k != 'password'} for u, data in users.items()}
    return jsonify(users_safe)

@admin_bp.route('/users/<username>', methods=['GET'])
@admin_login_required
def get_user(username):
    users = load_users()
    user = users.get(username)
    if not user:
        abort(404, description="User not found")
    user_safe = {k: v for k, v in user.items() if k != 'password'}
    return jsonify(user_safe)

@admin_bp.route('/users', methods=['POST'])
@admin_login_required
def create_user():
    data = request.json
    required_fields = ['username', 'password', 'complete_name', 'company_name', 'company_address', 'company_email', 'company_phone']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required user fields")
    users = load_users()
    username = data['username']
    if username in users:
        abort(400, description="User already exists")
    hashed_password = generate_password_hash(data['password'])
    users[username] = {
        'password': hashed_password,
        'complete_name': data['complete_name'],
        'company_name': data['company_name'],
        'company_address': data['company_address'],
        'company_email': data['company_email'],
        'company_phone': data['company_phone'],
        'company_logo': data.get('company_logo', None)
    }
    save_users(users)
    return jsonify({"message": "User created"}), 201

@admin_bp.route('/users/<username>', methods=['PUT'])
@admin_login_required
def update_user(username):
    data = request.json
    users = load_users()
    user = users.get(username)
    if not user:
        abort(404, description="User not found")
    # Update fields except password unless provided
    for field in ['complete_name', 'company_name', 'company_address', 'company_email', 'company_phone', 'company_logo']:
        if field in data:
            user[field] = data[field]
    if 'password' in data:
        user['password'] = generate_password_hash(data['password'])
    users[username] = user
    save_users(users)
    return jsonify({"message": "User updated"})

@admin_bp.route('/users/<username>', methods=['DELETE'])
@admin_login_required
def delete_user(username):
    users = load_users()
    if username not in users:
        abort(404, description="User not found")
    del users[username]
    save_users(users)
    return jsonify({"message": "User deleted"})

@admin_bp.route('/users/manage')
def manage_users():
    return render_template('users.html')
