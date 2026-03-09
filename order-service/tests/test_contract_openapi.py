# order-service/tests/test_contract_openapi.py
import pytest
import sys
import os
import yaml
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

# Загружаем OpenAPI контракт с правильной кодировкой
CONTRACT_PATH = Path(__file__).parent.parent.parent / 'contracts' / 'payment-api.yaml'
with open(CONTRACT_PATH, 'r', encoding='utf-8') as f:
    CONTRACT = yaml.safe_load(f)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_contract_amount_requirement():
    """Test that Order Service knows contract amount requirements"""
    
    # From contract we know amount must be > 0
    amount_schema = CONTRACT['paths']['/pay']['post']['requestBody']['content']['application/json']['schema']
    required_fields = amount_schema.get('required', [])
    
    assert 'amount' in required_fields, "Amount is required by contract"
    
    print("✅ Order Service knows amount is required")

def test_contract_expected_response_structure():
    """Test that Order Service expects correct response structure"""
    
    # Get expected response fields from contract
    response_schema = CONTRACT['paths']['/pay']['post']['responses']['200']['content']['application/json']['schema']
    required_fields = response_schema.get('required', [])
    
    assert 'payment_id' in required_fields
    assert 'amount' in required_fields
    assert 'status' in required_fields
    
    print(f"✅ Order Service expects fields: {required_fields}")

def test_contract_order_creation_with_mocks(client, mocker):
    """Test with mocks verifying contract compliance"""
    
    # Create mock response that matches contract
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'payment_id': 'pay_12345678',
        'amount': 100,
        'status': 'success'
    }
    mocker.patch('requests.post', return_value=mock_response)
    
    # Create order
    response = client.post('/order', json={'amount': 100})
    assert response.status_code == 201
    
    data = response.get_json()
    
    # Verify response structure
    assert 'order_id' in data
    assert 'payment_id' in data
    assert data['payment_id'] == 'pay_12345678'
    assert 'amount' in data
    assert data['amount'] == 100
    
    print("✅ Order Service correctly processes payment response")