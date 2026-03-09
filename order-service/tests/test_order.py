import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import requests

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
    assert data['service'] == 'order'

def test_create_order_success(client, mocker):
    """Тест: успешное создание заказа"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'payment_id': 'pay123', 'amount': 100}
    mocker.patch('requests.post', return_value=mock_response)
    
    response = client.post('/order', json={'amount': 100})
    assert response.status_code == 201
    data = response.get_json()
    assert 'order_id' in data
    assert data['payment_id'] == 'pay123'
    assert data['amount'] == 100
    assert data['status'] == 'paid'

def test_create_order_no_amount(client):
    """Тест: создание заказа без суммы"""
    response = client.post('/order', json={})
    assert response.status_code == 400

def test_create_order_zero_amount(client):
    """Тест: создание заказа с нулевой суммой"""
    response = client.post('/order', json={'amount': 0})
    assert response.status_code == 400

def test_create_order_negative_amount(client):
    """Тест: создание заказа с отрицательной суммой"""
    response = client.post('/order', json={'amount': -50})
    assert response.status_code == 400

def test_create_order_payment_failed(client, mocker):
    """Тест: платеж не прошел"""
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mocker.patch('requests.post', return_value=mock_response)
    
    response = client.post('/order', json={'amount': 100})
    assert response.status_code == 402

def test_create_order_payment_unavailable(client, mocker):
    """Тест: Payment Service недоступен"""
    mocker.patch('requests.post', side_effect=requests.exceptions.ConnectionError)
    
    response = client.post('/order', json={'amount': 100})
    assert response.status_code == 503

def test_get_order_success(client, mocker):
    """Тест: получение существующего заказа"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'payment_id': 'pay123', 'amount': 100}
    mocker.patch('requests.post', return_value=mock_response)
    
    create_resp = client.post('/order', json={'amount': 100})
    order_data = create_resp.get_json()
    order_id = order_data['order_id']
    
    get_resp = client.get(f'/order/{order_id}')
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['order_id'] == order_id

def test_get_order_not_found(client):
    """Тест: получение несуществующего заказа"""
    response = client.get('/order/12345678')
    assert response.status_code == 404