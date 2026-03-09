from flask import Flask, jsonify, request
import requests
import os
import uuid

app = Flask(__name__)

PAYMENT_URL = os.getenv('PAYMENT_URL', 'http://localhost:5001')
orders = {}

@app.route('/order', methods=['POST'])
def create_order():
    """Создает заказ и вызывает платежный сервис"""
    order_data = request.json
    
    if not order_data or 'amount' not in order_data:
        return jsonify({'error': 'Amount is required'}), 400
    
    if order_data['amount'] <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    
    order_id = str(uuid.uuid4())[:8]
    
    try:
        payment_response = requests.post(
            f"{PAYMENT_URL}/pay",
            json={'amount': order_data['amount']},
            timeout=5
        )
        
        if payment_response.status_code == 200:
            payment_data = payment_response.json()
            
            orders[order_id] = {
                'order_id': order_id,
                'amount': order_data['amount'],
                'payment_id': payment_data['payment_id'],
                'status': 'paid'
            }
            
            return jsonify(orders[order_id]), 201
        else:
            return jsonify({'error': 'Payment failed'}), 402
            
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Payment service unavailable'}), 503

@app.route('/order/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'order'})

if __name__ == '__main__':
    app.run(port=5002, debug=True)