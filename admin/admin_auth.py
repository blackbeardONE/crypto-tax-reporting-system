from flask import Blueprint, request, session, redirect, url_for, render_template
from functools import wraps

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin/auth')

# For demo, simple admin user store
admin_users = {
    "admin": {
        "password": "adminpass"
    }
}

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_username' not in session:
            return redirect(url_for('admin_auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = admin_users.get(username)
        if user and user['password'] == password:
            session['admin_username'] = username
            return redirect(url_for('admin_auth.dashboard'))
        else:
            error = "Invalid admin username or password"
            return render_template('admin_login.html', error=error)
    return render_template('admin_login.html')

@admin_auth_bp.route('/logout')
def logout():
    session.pop('admin_username', None)
    return redirect(url_for('admin_auth.login'))

@admin_auth_bp.route('/dashboard')
@admin_login_required
def dashboard():
    return render_template('admin_dashboard.html')
