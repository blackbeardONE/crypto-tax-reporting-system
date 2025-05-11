from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from admin.admin_auth import admin_login_required
import os
import logging

log_viewer_bp = Blueprint('log_viewer', __name__, url_prefix='/admin/logs')

LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'terminusa.log')

@log_viewer_bp.before_request
def require_admin_login():
    if not session.get('username'):
        return redirect(url_for('admin_auth.login'))

@log_viewer_bp.route('/', methods=['GET'])
@admin_login_required
def view_logs():
    return render_template('log_viewer.html')

@log_viewer_bp.route('/fetch', methods=['GET'])
@admin_login_required
def fetch_logs():
    try:
        with open(LOG_FILE_PATH, 'r') as f:
            lines = f.readlines()
        # Return last 100 lines by default
        last_lines = lines[-100:]
        return jsonify({'logs': last_lines})
    except Exception as e:
        logging.error(f"Error reading log file: {e}")
        return jsonify({'error': 'Could not read log file'}), 500
