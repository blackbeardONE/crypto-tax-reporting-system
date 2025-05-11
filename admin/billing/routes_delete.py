from flask import jsonify, abort
from db import SessionLocal, BillingRecord
from logger import setup_logger
from . import billing_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

@billing_bp.route('/invoices/<int:invoice_id>', methods=['DELETE'])
@admin_login_required
def delete_invoice(invoice_id):
    db = SessionLocal()
    invoice = db.query(BillingRecord).filter(BillingRecord.id == invoice_id).first()
    if not invoice:
        db.close()
        logger.warning(f"Invoice {invoice_id} not found for deletion")
        abort(404, description="Invoice not found")
    db.delete(invoice)
    db.commit()
    db.close()
    logger.info(f"Deleted invoice {invoice_id}")
    return jsonify({"message": "Invoice deleted"})
