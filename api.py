from flask import Blueprint, request, jsonify, session
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# In-memory user data store for demonstration
users = {
    'admin': {
        'username': 'admin',
        'complete_name': 'Admin User',
        'company_name': 'Terminusa Inc.',
        'email': 'admin@terminusa.com',
        'phone': '',
        'password': 'password123'  # In production, use hashed passwords
    }
}

# User settings endpoints
@api_bp.route('/user/settings', methods=['GET'])
@login_required
def get_user_settings():
    username = session['username']
    user = users.get(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user_data = {k: v for k, v in user.items() if k != 'password'}
    return jsonify(user_data)

@api_bp.route('/user/settings', methods=['POST'])
@login_required
def update_user_settings():
    username = session['username']
    user = users.get(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.json

    # Validate email
    email = data.get('company_email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Validate password confirmation
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    if password or confirm_password:
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        if password:
            user['password'] = password  # In production, hash the password

    # Update allowed fields
    for field in ['complete_name', 'company_name', 'email', 'phone']:
        if field in data:
            # Map company_email to email in user dict
            if field == 'email' and 'company_email' in data:
                user['email'] = data['company_email']
            else:
                user[field] = data[field]

    return jsonify({'message': 'User settings updated'})

# Billing endpoints (mock implementation)
@api_bp.route('/billing/subscription', methods=['GET'])
@login_required
def get_subscription():
    # Return mock subscription info
    return jsonify({
        'plan': 'Free Tier',
        'monthly_price': 0,
        'features': ['Basic report generation', 'limited API calls']
    })

@api_bp.route('/billing/history', methods=['GET'])
@login_required
def get_billing_history():
    # Return mock billing history
    history = [
        {'date': '2025-04-01', 'amount': 0, 'transaction_id': 'TX123456789', 'status': 'Completed'},
        {'date': '2025-03-01', 'amount': 10, 'transaction_id': 'TX987654321', 'status': 'Completed'}
    ]
    return jsonify(history)

@api_bp.route('/billing/payment-methods', methods=['GET'])
@login_required
def get_payment_methods():
    # Return mock payment methods
    return jsonify([])

@api_bp.route('/billing/payment-methods', methods=['POST'])
@login_required
def add_payment_method():
    data = request.json
    # In production, validate and store payment method securely
    return jsonify({'message': 'Payment method added'})

# MFA endpoints (mock)
@api_bp.route('/mfa/status', methods=['GET'])
@login_required
def get_mfa_status():
    return jsonify({'enabled': True})

@api_bp.route('/mfa/verify', methods=['POST'])
@login_required
def verify_mfa():
    data = request.json
    code = data.get('code')
    # Mock verification
    if code == '123456':
        return jsonify({'verified': True})
    else:
        return jsonify({'verified': False}), 400

# Report management endpoints (mock)
@api_bp.route('/reports', methods=['GET'])
@login_required
def list_reports():
    # Return mock report list
    reports = [
        {'id': 1, 'name': 'Tax Report April 2025', 'date': '2025-04-10'},
        {'id': 2, 'name': 'Tax Report March 2025', 'date': '2025-03-10'}
    ]
    return jsonify(reports)

@api_bp.route('/reports/<int:report_id>', methods=['GET'])
@login_required
def get_report(report_id):
    # Return mock report content
    if report_id == 1:
        content = 'Report content for April 2025'
    elif report_id == 2:
        content = 'Report content for March 2025'
    else:
        return jsonify({'error': 'Report not found'}), 404
    return jsonify({'id': report_id, 'content': content})
