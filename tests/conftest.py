import pytest
from aiohttp import web
from app.auth import create_access_token, token_required
from app.routes import login, add_book


@pytest.fixture
async def client(aiohttp_client):
    """Фикстура для создания тестового клиента.

        Эта фикстура создает временное приложение `aiohttp` для тестирования маршрутов,
        таких как вход в систему и добавление книги. Также добавляет защищенный маршрут,
        который требует токен для доступа.

        Args:
            aiohttp_client: Фикстура для создания клиента, который можно использовать для
            отправки запросов к приложению.

        Returns:
            aiohttp.ClientSession: Клиент, который может использоваться для тестирования
            API приложения.
        """
    app = web.Application()
    app.router.add_post("/login", login)
    app.router.add_post("/books", add_book)

    # Добавляем пример функции, защищенной токеном
    @token_required
    async def protected_handler(request):
        return web.json_response({"message": "Success"})

    app.router.add_get("/protected", protected_handler)

    return await aiohttp_client(app)


@pytest.fixture
def mock_access_token():
    return create_access_token({
        "username": "user",
        "password": "password"
    })
