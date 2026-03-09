import pytest
import sys
import os
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

def test_contract_amount_requirement():
    """Проверка требований к amount"""
    
    # Amount > 0
    amount_schema = CONTRACT['paths']['/pay']['post']['requestBody']['content']['application/json']['schema']
    required_fields = amount_schema.get('required', [])
    
    assert 'amount' in required_fields, "Amount is required by contract"
    
    print("OK")

def test_contract_expected_response_structure():
    """Проверка структуры ответа"""
    
    response_schema = CONTRACT['paths']['/pay']['post']['responses']['200']['content']['application/json']['schema']
    required_fields = response_schema.get('required', [])
    
    assert 'payment_id' in required_fields
    assert 'amount' in required_fields
    assert 'status' in required_fields
    
    print(f"OK: {required_fields}")

def test_contract_order_creation_with_mocks(client, mocker):
    """Тестирование с помощью макетов, подтверждающих соответствие контракту"""
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'payment_id': 'pay_12345678',
        'amount': 100,
        'status': 'success'
    }
    mocker.patch('requests.post', return_value=mock_response)
    
    response = client.post('/order', json={'amount': 100})
    assert response.status_code == 201
    
    data = response.get_json()
    
    assert 'order_id' in data
    assert 'payment_id' in data
    assert data['payment_id'] == 'pay_12345678'
    assert 'amount' in data
    assert data['amount'] == 100
    
    print("OK")