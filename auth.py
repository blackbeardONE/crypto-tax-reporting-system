import logging
import smtplib
import uuid
import toml
from email.mime.text import MIMEText
from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from db import SessionLocal, User

auth_bp = Blueprint('auth', __name__)

logger = logging.getLogger('auth')

# Load SMTP config from config.toml
config = toml.load('config.toml')
smtp_config = config.get('smtp', {})

SMTP_SERVER = smtp_config.get('server', 'smtp.example.com')
SMTP_PORT = smtp_config.get('port', 587)
SMTP_USERNAME = smtp_config.get('username', 'your-email@example.com')
SMTP_PASSWORD = smtp_config.get('password', 'your-email-password')
EMAIL_FROM = smtp_config.get('email_from', 'no-reply@example.com')
EMAIL_SUBJECT = smtp_config.get('email_subject', 'Password Reset Request')

import time

def send_email(to_email, subject, body, max_retries=3, retry_delay=2):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email

    attempt = 0
    while attempt < max_retries:
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(EMAIL_FROM, [to_email], msg.as_string())
            logger.info(f"Password reset email sent to {to_email} on attempt {attempt + 1}")
            return True
        except Exception as e:
            attempt += 1
            logger.error(f"Failed to send email to {to_email} on attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
    logger.error(f"All {max_retries} attempts to send email to {to_email} failed.")
    return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            logger.info("Unauthorized access attempt to a protected route")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.info(f"Login attempt for user: {username}")
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        if user and check_password_hash(user.password_hash, password):
            session['username'] = username
            db.close()
            logger.info(f"User {username} logged in successfully")
            if user.is_admin:
                return redirect(url_for('admin_auth.dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            db.close()
            logger.warning(f"Failed login attempt for user: {username}")
            error = "Invalid username or password"
            return render_template('login.html', error=error)
    return render_template('login.html')

# In-memory token store for demo purposes
password_reset_tokens = {}

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        logger.info(f"Password reset requested for email: {email}")
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.company_email == email).first()
            if user:
                token = str(uuid.uuid4())
                password_reset_tokens[token] = user.username
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                email_body = f"""
                <p>Hello {user.complete_name},</p>
                <p>You requested a password reset. Click the link below to reset your password:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>If you did not request this, please ignore this email.</p>
                """
                if not send_email(email, EMAIL_SUBJECT, email_body):
                    logger.error(f"Failed to send password reset email to {email}")
            else:
                logger.warning(f"Password reset requested for non-existent email: {email}")
        except Exception as e:
            logger.error(f"Exception during password reset process for email {email}: {e}")
        finally:
            db.close()
        message = "If this email is registered, a password reset link has been sent."
        return render_template('forgot_password.html', message=message)
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    username = password_reset_tokens.get(token)
    if not username:
        flash("Invalid or expired password reset token.", "danger")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        new_password = request.form.get('password')
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.commit()
            flash("Your password has been reset successfully. Please log in.", "success")
            password_reset_tokens.pop(token, None)
            db.close()
            return redirect(url_for('auth.login'))
        db.close()
        flash("User not found.", "danger")
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', token=token)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        complete_name = request.form.get('complete_name')
        company_name = request.form.get('company_name')
        company_address = request.form.get('company_address')
        company_email = request.form.get('company_email')
        company_phone = request.form.get('company_phone')
        company_logo = request.files.get('company_logo')

        logger.info(f"Registration attempt for user: {username}")

        db = SessionLocal()
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            db.close()
            logger.warning(f"Registration failed: Username {username} already exists")
            error = "Username already exists"
            return render_template('registration.html', error=error)

        logo_filename = None
        if company_logo:
            import os
            upload_folder = os.path.join('static', 'images')
            os.makedirs(upload_folder, exist_ok=True)
            logo_filename = os.path.join(upload_folder, 'terminusa_logo.png')
            company_logo.save(logo_filename)

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            complete_name=complete_name,
            company_name=company_name,
            company_address=company_address,
            company_email=company_email,
            company_phone=company_phone,
            company_logo=logo_filename
        )
        db.add(new_user)
        db.commit()
        db.close()

        session['username'] = username
        logger.info(f"User {username} registered successfully")
        return redirect(url_for('dashboard'))
    return render_template('registration.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = session.get('username')
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.close()
        logger.warning(f"Profile access for non-existent user: {username}")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        complete_name = request.form.get('complete_name')
        company_name = request.form.get('company_name')
        company_address = request.form.get('company_address')
        company_email = request.form.get('company_email')
        company_phone = request.form.get('company_phone')
        company_logo = request.files.get('company_logo')

        user.complete_name = complete_name
        user.company_name = company_name
        user.company_address = company_address
        user.company_email = company_email
        user.company_phone = company_phone

        if company_logo:
            import os
            upload_folder = os.path.join('static', 'images')
            os.makedirs(upload_folder, exist_ok=True)
            logo_filename = os.path.join(upload_folder, 'terminusa_logo.png')
            company_logo.save(logo_filename)
            user.company_logo = logo_filename

        db.commit()
        db.close()
        logger.info(f"Profile updated for user: {username}")
        message = "Profile updated successfully."
        return render_template('profile.html', user=user, message=message)

    db.close()
    return render_template('profile.html', user=user)

@auth_bp.route('/logout')
def logout():
    username = session.get('username')
    logger.info(f"User {username} logged out")
    session.pop('username', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/test-email')
def test_email():
    test_recipient = "your-email@example.com"  # Replace with your email to test
    test_subject = "Test Email from Terminusa"
    test_body = "<p>This is a test email sent from the Terminusa application to verify SMTP configuration.</p>"
    success = send_email(test_recipient, test_subject, test_body)
    if success:
        return "Test email sent successfully."
    else:
        return "Failed to send test email."
