import pytest
import httpx

'''
    e2e тесты для проверки работы всей системы в целом, для этого должны быть запущены
    все компоненты страховой компании. На данный момент это база данных, icp клиент и
    бэкенда страховой компании
'''

def test_ping():
    with httpx.Client(base_url="http://localhost:8001") as client:
        response = client.get("/ping")
        
        assert response.status_code == 200
        
        assert response.json() == {"message": "Hello world"}

def test_authorize():
    with httpx.Client(base_url="http://localhost:8001") as client:
        response = client.post(
            "/v1/authorize",
            json={
                'login': 'alfa',
                'password': 'alfa'
            }
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        
        response = client.post(
            "/v1/authorize",
            json={
                'login': 'beta',
                'password': 'alfa'
            }
        )
        
        assert response.status_code == 400
        assert "message" in response.json()
        assert response.json()['message'] == 'No such login exists'
        
        response = client.post(
            "/v1/authorize",
            json={
                'login': 'alfa',
                'password': 'wrong_password'
            }
        )
        
        assert response.status_code == 400
        assert "message" in response.json()
        assert response.json()['message'] == 'Invalid password'

def test_user():
    with httpx.Client(base_url="http://localhost:8001") as client:
        # Сначала авторизуемся
        auth_response = client.post(
            "/v1/authorize",
            json={
                'login': 'alfa',
                'password': 'alfa'
            }
        )
        assert auth_response.status_code == 200
        token = auth_response.json()['access_token']

        # Тестируем получение информации о пользователе
        # Успешный случай
        response = client.get(
            "/v1/user",
            params={"email": "b@b.ru"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "user" in response.json()
