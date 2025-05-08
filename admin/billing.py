from flask import Blueprint, request, jsonify, abort
import os
import json

billing_bp = Blueprint('billing', __name__, url_prefix='/admin/billing')

BILLING_FILE = os.path.join(os.path.dirname(__file__), 'billing.json')

def load_billing():
    if not os.path.exists(BILLING_FILE):
        return {}
    with open(BILLING_FILE, 'r') as f:
        return json.load(f)

def save_billing(billing):
    with open(BILLING_FILE, 'w') as f:
        json.dump(billing, f, indent=4)

@billing_bp.route('/invoices', methods=['GET'])
def get_invoices():
    billing = load_billing()
    return jsonify(billing.get('invoices', []))

@billing_bp.route('/invoices/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    billing = load_billing()
    invoices = billing.get('invoices', [])
    invoice = next((inv for inv in invoices if inv['id'] == invoice_id), None)
    if not invoice:
        abort(404, description="Invoice not found")
    return jsonify(invoice)

@billing_bp.route('/invoices', methods=['POST'])
def create_invoice():
    data = request.json
    required_fields = ['id', 'username', 'amount', 'date', 'status']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required invoice fields")
    billing = load_billing()
    invoices = billing.get('invoices', [])
    if any(inv['id'] == data['id'] for inv in invoices):
        abort(400, description="Invoice ID already exists")
    invoices.append({
        'id': data['id'],
        'username': data['username'],
        'amount': data['amount'],
        'date': data['date'],
        'status': data['status']
    })
    billing['invoices'] = invoices
    save_billing(billing)
    return jsonify({"message": "Invoice created"}), 201

@billing_bp.route('/invoices/<invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    data = request.json
    billing = load_billing()
    invoices = billing.get('invoices', [])
    invoice = next((inv for inv in invoices if inv['id'] == invoice_id), None)
    if not invoice:
        abort(404, description="Invoice not found")
    for field in ['username', 'amount', 'date', 'status']:
        if field in data:
            invoice[field] = data[field]
    save_billing(billing)
    return jsonify({"message": "Invoice updated"})

@billing_bp.route('/invoices/<invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    billing = load_billing()
    invoices = billing.get('invoices', [])
    new_invoices = [inv for inv in invoices if inv['id'] != invoice_id]
    if len(new_invoices) == len(invoices):
        abort(404, description="Invoice not found")
    billing['invoices'] = new_invoices
    save_billing(billing)
    return jsonify({"message": "Invoice deleted"})
