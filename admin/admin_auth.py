from flask import Blueprint, request, session, redirect, url_for, render_template
from functools import wraps
from db import SessionLocal, User
from werkzeug.security import check_password_hash

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin/auth')

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username')
        if not username:
            return redirect(url_for('auth.login'))
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()
        if not user or not user.is_admin:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Removed admin login route to unify login process with main auth blueprint
# @admin_auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         db = SessionLocal()
#         user = db.query(User).filter(User.username == username).first()
#         if user and user.is_admin and check_password_hash(user.password_hash, password):
#             session['username'] = username
#             db.close()
#             return redirect(url_for('admin_auth.dashboard'))
#         else:
#             db.close()
#             error = "Invalid admin username or password"
#             return render_template('admin_login.html', error=error)
#     return render_template('admin_login.html')

@admin_auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))

@admin_auth_bp.route('/dashboard')
@admin_login_required
def dashboard():
    return render_template('admin_dashboard.html')

@admin_auth_bp.route('/dashboard_home')
@admin_login_required
def dashboard_home():
    return render_template('visualizations.html')
