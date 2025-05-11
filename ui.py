from flask import Flask, render_template, request, redirect, url_for, session
import threading
import os
import logging
from main import main as run_terminusa_main
from auth import auth_bp
from admin.user_management import admin_bp

import os
from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader

template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
admin_template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin', 'templates')

app = Flask(__name__)
app.secret_key = os.urandom(24)

template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
admin_template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin', 'templates')

# Set up Jinja2 loader to load templates from both templates and admin/templates directories
from jinja2 import ChoiceLoader, FileSystemLoader
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(template_path),
    FileSystemLoader(admin_template_path),
])

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
from admin.subscription_management import subscription_bp
from admin.billing import billing_bp
from admin.admin_auth import admin_auth_bp
from api import api_bp
from admin.reports import reports_bp
from admin.analytics import analytics_bp
from admin.frontend_settings import frontend_settings_bp
from admin.log_viewer import log_viewer_bp

app.register_blueprint(subscription_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(admin_auth_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(frontend_settings_bp)
app.register_blueprint(log_viewer_bp)
app.register_blueprint(api_bp)
logger = logging.getLogger('terminusa_logger')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('landing.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    from db import SessionLocal, User
    username = session.get('username')
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user and user.is_admin:
        return redirect(url_for('admin_auth.dashboard'))
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if user_id:
            # Run the Terminusa main function in a separate thread to avoid blocking
            thread = threading.Thread(target=run_terminusa_main_with_user_id, args=(user_id,))
            thread.start()
            return redirect(url_for('status', user_id=user_id))
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    from flask import redirect
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.register'))

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    username = session.get('username')
    # Fetch user data from api or in-memory store
    from flask import jsonify
    import requests
    # For simplicity, call internal function directly (in production, use service layer)
    from api import users
    user = users.get(username)
    if not user:
        return redirect(url_for('auth.login'))
    # Prepare user data for template
    user_data = {
        'username': user.get('username'),
        'complete_name': user.get('complete_name', ''),
        'company_name': user.get('company_name', ''),
        'company_email': user.get('email', ''),
        'company_phone': user.get('phone', '')
    }
    return render_template('profile.html', user=user_data)

@app.route('/mfa', methods=['GET'])
@login_required
def mfa():
    return render_template('mfa.html')

@app.route('/help', methods=['GET'])
@login_required
def help():
    return render_template('help.html')

# In-memory store for report status and data keyed by user_id
report_store = {}

@app.route('/status/<user_id>')
@login_required
def status(user_id):
    # Return current report status or default message
    return report_store.get(user_id, f"Processing tax report for user: {user_id}. Check logs for progress.")

def run_terminusa_main_with_user_id(user_id):
    import builtins
    import sys
    import io

    original_input = builtins.input
    builtins.input = lambda prompt='': user_id

    # Capture stdout to store logs
    captured_output = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = captured_output

    try:
        run_terminusa_main()
    except Exception as e:
        logger.error(f"Error running Terminusa main: {e}")
        report_store[user_id] = f"Error during report generation: {e}"
    else:
        # On success, store the full output
        report_store[user_id] = captured_output.getvalue()
    finally:
        builtins.input = original_input
        sys.stdout = sys_stdout

if __name__ == '__main__':
    app.run(debug=True, port=5000)
