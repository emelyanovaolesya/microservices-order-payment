from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

payments = {}

@app.route('/pay', methods=['POST'])
def process_payment():
    data = request.json
    
    if not data or 'amount' not in data:
        return jsonify({'error': 'Amount is required'}), 400
    
    amount = data['amount']
    
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400

    payment_id = str(uuid.uuid4())[:8]
    
    payments[payment_id] = {
        'payment_id': payment_id,
        'amount': amount,
        'status': 'success'
    }
    
    return jsonify(payments[payment_id]), 200

@app.route('/payment/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = payments.get(payment_id)
    if payment:
        return jsonify(payment)
    return jsonify({'error': 'Payment not found'}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'payment'})

if __name__ == '__main__':
    app.run(port=5001, debug=True)