from app.auth import create_access_token
from app.config import SECRET_KEY
import jwt
import pytest


def test_create_access_token():
    token = create_access_token({"username": "user"})
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert decoded_token["username"] == "user"
    assert "exp" in decoded_token


@pytest.mark.asyncio
async def test_protected_handler_with_valid_token(client):
    """Тестирование защищенного обработчика с действительным токеном.

        Сначала выполняем вход, чтобы получить токен, а затем используем
        этот токен для доступа к защищенному маршруту.
        """
    response = await client.post("/login", json={"username": "user", "password": "password"})
    assert response.status == 200
    token = await response.json()

    response = await client.get("/protected", headers={"Authorization": f"Bearer {token['access_token']}"})
    assert response.status == 200
    data = await response.json()
    assert data == {"message": "Success"}

@pytest.mark.asyncio
async def test_protected_handler_without_token(client):
    """Тестирование защищенного обработчика без токена.

        Проверяет, что доступ к защищенному маршруту без токена
        возвращает ошибку 401 Unauthorized.
        """
    response = await client.get("/protected")
    assert response.status == 401
    assert await response.text() == "Missing authorization token"


@pytest.mark.asyncio
async def test_protected_handler_with_invalid_token(client):
    """Тестирование защищенного обработчика с недействительным токеном.

        Проверяет, что доступ к защищенному маршруту с недействительным
        токеном возвращает ошибку 401 Unauthorized.
        """
    response = await client.get("/protected", headers={"Authorization": "Bearer invalid_token"})
    assert response.status == 401
    text = await response.text()
    assert text in ["Token expired", "Invalid token"]