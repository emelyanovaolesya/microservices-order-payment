import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Тест: проверка здоровья сервиса"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'payment'

def test_payment_success(client):
    """Тест: успешное создание платежа"""
    response = client.post('/pay', json={'amount': 100})
    assert response.status_code == 200
    data = response.get_json()
    assert 'payment_id' in data
    assert data['amount'] == 100
    assert data['status'] == 'success'

def test_payment_no_amount(client):
    """Тест: создание платежа без суммы"""
    response = client.post('/pay', json={})
    assert response.status_code == 400

def test_payment_zero_amount(client):
    """Тест: создание платежа с нулевой суммой"""
    response = client.post('/pay', json={'amount': 0})
    assert response.status_code == 400

def test_payment_negative_amount(client):
    """Тест: создание платежа с отрицательной суммой"""
    response = client.post('/pay', json={'amount': -50})
    assert response.status_code == 400

def test_get_payment_success(client):
    """Тест: получение существующего платежа"""
    create_resp = client.post('/pay', json={'amount': 150})
    payment_data = create_resp.get_json()
    payment_id = payment_data['payment_id']
    
    get_resp = client.get(f'/payment/{payment_id}')
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['payment_id'] == payment_id
    assert data['amount'] == 150

def test_get_payment_not_found(client):
    """Тест: получение несуществующего платежа"""
    response = client.get('/payment/12345678')
    assert response.status_code == 404