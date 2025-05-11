from flask import jsonify, abort, session, redirect, url_for
from db import SessionLocal, BillingRecord, User
from logger import setup_logger
from . import billing_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

@billing_bp.before_request
def require_admin_login():
    if not session.get('username'):
        return redirect(url_for('auth.login'))

@billing_bp.route('/invoices', methods=['GET'])
@admin_login_required
def get_invoices():
    db = SessionLocal()
    invoices = db.query(BillingRecord).all()
    result = []
    for inv in invoices:
        result.append({
            'id': inv.id,
            'username': inv.user.username if inv.user else None,
            'amount': inv.amount,
            'date': inv.billing_date.strftime('%Y-%m-%d'),
            'status': inv.description
        })
    db.close()
    logger.info("Fetched all invoices")
    return jsonify(result)

@billing_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@admin_login_required
def get_invoice(invoice_id):
    db = SessionLocal()
    invoice = db.query(BillingRecord).filter(BillingRecord.id == invoice_id).first()
    if not invoice:
        db.close()
        logger.warning(f"Invoice {invoice_id} not found")
        abort(404, description="Invoice not found")
    result = {
        'id': invoice.id,
        'username': invoice.user.username if invoice.user else None,
        'amount': invoice.amount,
        'date': invoice.billing_date.strftime('%Y-%m-%d'),
        'status': invoice.description
    }
    db.close()
    logger.info(f"Fetched invoice {invoice_id}")
    return jsonify(result)
