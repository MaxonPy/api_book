import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_login_success(client):
    """Тестирование успешного входа пользователя.

        Отправляет POST-запрос на конечную точку "/login" с правильными учетными данными.
        Проверяет, что статус ответа равен 200, и что в ответе содержится токен доступа.

        Args:
            client: Фикстура для клиентских запросов.

        Asserts:
            Проверяет, что статус ответа 200, токен доступа присутствует и является строкой, а также не пуст.
        """

    response = await client.post("/login", json={"username": "user", "password": "password"})
    assert response.status == 200
    data = await response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)  # Проверяем, что токен является строкой
    assert len(data["access_token"]) > 0  # Проверяем, что токен не пустой


@pytest.mark.asyncio
async def test_login_failure(client):
    """Тестирование неудачного входа пользователя.

        Отправляет POST-запрос на конечную точку "/login" с неправильными учетными данными.
        Проверяет, что статус ответа равен 401 (Unauthorized).

        Args:
            client: Фикстура для клиентских запросов.

        Asserts:
            Проверяет, что статус ответа 401.
        """

    response = await client.post("/login", json={"username": "wrong", "password": "password"})
    assert response.status == 401


@pytest.mark.asyncio
async def test_add_book(client, mock_access_token, mocker):
    """Тестирование добавления книги в базу данных.

        Отправляет POST-запрос на конечную точку "/books" с данными новой книги.
        Проверяет, что книга успешно добавлена, статус ответа равен 200, и возвращаемые данные соответствуют ожиданиям.

        Args:
            client: Фикстура для клиентских запросов.
            mock_access_token: Мокированный токен доступа для авторизации.
            mocker: Фикстура для создания моков.

        Asserts:
            Проверяет, что статус ответа 200, ID и заголовок книги соответствуют ожидаемым значениям.
        """

    mock_add_book_to_db = mocker.patch("app.db.add_book_to_db", return_value={"id": 1, "title": "Test Book"})
    headers = {"Authorization": f"Bearer {mock_access_token}"}
    response = await client.post("/books", headers=headers, json={
        "title": "Test Book",
        "author": "Test Author",
        "year": 2021,
        "isbn": "1234567890123"
    })
    assert response.status == 200
    data = await response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Book"


@pytest.mark.asyncio
async def test_get_books(client, mock_access_token, mocker):
    """Тестирование получения списка книг.

        Отправляет GET-запрос на конечную точку "/books" и проверяет, что статус ответа равен 200
        и возвращаемые данные соответствуют ожидаемым значениям.

        Args:
            client: Фикстура для клиентских запросов.
            mock_access_token: Мокированный токен доступа для авторизации.
            mocker: Фикстура для создания моков.

        Asserts:
            Проверяет, что статус ответа 200, и количество книг в ответе соответствует ожиданиям.
        """
    mock_get_books_from_db = mocker.patch("app.db.get_books_from_db", return_value=[
        {"id": 1, "title": "Test Book", "author": "Author", "year": 2021, "isbn": "1234567890123"}
    ])
    headers = {"Authorization": f"Bearer {mock_access_token}"}
    response = await client.get("/books", headers=headers)
    assert response.status == 200
    data = await response.json()
    assert len(data["books"]) == 1


@pytest.mark.asyncio
async def test_delete_book(client, mock_access_token, mocker):
    """Тестирование удаления книги из базы данных.

        Отправляет DELETE-запрос на конечную точку "/books/{id}" и проверяет,
        что статус ответа равен 200 и книга была успешно удалена.

        Args:
            client: Фикстура для клиентских запросов.
            mock_access_token: Мокированный токен доступа для авторизации.
            mocker: Фикстура для создания моков.

        Asserts:
            Проверяет, что статус ответа 200 и статус удаления книги соответствует ожиданиям.
        """

    mock_delete_book_from_db = mocker.patch("app.db.delete_book_from_db", return_value={"status": "success"})
    headers = {"Authorization": f"Bearer {mock_access_token}"}
    response = await client.delete("/books/1", headers=headers)
    assert response.status == 200
    data = await response.json()
    assert data["status"] == "Book deleted successfully"


@pytest.mark.asyncio
async def test_add_book(client, mock_access_token):
    """Тестирование добавления новой книги.

        Отправляет POST-запрос на конечную точку "/books" с данными новой книги
        и проверяет, что книга успешно добавлена.

        Args:
            client: Фикстура для клиентских запросов.
            mock_access_token: Мокированный токен доступа для авторизации.

        Asserts:
            Проверяет, что статус ответа 200, ID и заголовок книги соответствуют ожидаемым значениям.
        """

    new_book_data = {
        "title": "Тестовая книга",
        "author": "Имя Автора",
        "year": 2021,
        "isbn": "1234567890123"
    }


    headers = {
        "Authorization": f"Bearer {mock_access_token}"
    }

    # мок вызова к базе данных для добавления книги
    with patch("app.db.add_book_to_db", new_callable=AsyncMock) as mock_add_book:
        mock_add_book.return_value = {"id": 1, **new_book_data}  # Симулируем успешное добавление

        response = await client.post("/books", json=new_book_data, headers=headers)

        assert response.status == 200
        response_data = await response.json()
        assert response_data["id"] == 1
        assert response_data["title"] == new_book_data["title"]
        assert response_data["author"] == new_book_data["author"]