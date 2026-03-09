import pytest
import sys
import os
import json
import yaml
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

CONTRACT_PATH = Path(__file__).parent.parent.parent / 'contracts' / 'payment-api.yaml'
with open(CONTRACT_PATH, 'r', encoding='utf-8') as f:
    CONTRACT = yaml.safe_load(f)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_contract_payment_creation_success(client):
    """Проверка успешного создания платежа"""
    
    response = client.post('/pay', json={'amount': 100.50})
    assert response.status_code == 200
    
    data = response.get_json()
    
    assert 'payment_id' in data, "Response must contain payment_id"
    assert data['amount'] == 100.50, f"Amount should be 100.50, got {data['amount']}"
    assert data['status'] in ['success', 'pending', 'failed'], f"Status {data['status']} not allowed"
    
    print("OK")

def test_contract_payment_creation_error(client):
    """Проверка неуспешного создания"""
    
    response = client.post('/pay', json={'amount': -10})
    assert response.status_code == 400
    
    data = response.get_json()
    
    assert 'error' in data, "Error response must contain error field"
    
    print("OK")

def test_contract_get_payment_success(client):
    """Проверка получения платежа"""
    
    create_resp = client.post('/pay', json={'amount': 200})
    payment_data = create_resp.get_json()
    payment_id = payment_data['payment_id']
    
    response = client.get(f'/payment/{payment_id}')
    assert response.status_code == 200
    
    data = response.get_json()

    assert 'payment_id' in data
    assert data['payment_id'] == payment_id
    assert 'amount' in data
    assert 'status' in data
    
    print(f"OK, ID={payment_id}")

def test_contract_get_payment_not_found(client):
    """Проверка 404"""
    
    response = client.get('/payment/pay_99999999')
    assert response.status_code == 404
    
    data = response.get_json()
    
    assert 'error' in data
    
    print("OK")

def test_contract_validate_amount_zero(client):
    """Проверка суммы по контракту"""
    
    response = client.post('/pay', json={'amount': 0})
    assert response.status_code == 400 
    
    print("OK")