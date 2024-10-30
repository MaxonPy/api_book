from aiohttp import web
from app.auth import create_access_token, token_required
from .models import Book
from app.db import add_book_to_db, delete_book_from_db, get_books_from_db

async def login(request):
    """Обработчик для логина пользователя.

        Проверяет предоставленные учетные данные и, если они верны,
        создает токен доступа.

        Args:
            request: Объект запроса Aiohttp.

        Returns:
            web.json_response: Ответ с токеном доступа или ошибка 401.
        """
    data = await request.json()
    if data.get("username") == "user" and data.get("password") == "password":
        token = create_access_token({"username": data["username"]})
        return web.json_response({"access_token": token})
    return web.HTTPUnauthorized(text="Invalid credentials")



@token_required
async def add_book(request):
    """Обработчик для добавления новой книги.

        Обрабатывает запрос на добавление книги в базу данных.
        Необходим токен доступа для выполнения этой операции.

        Args:
            request: Объект запроса Aiohttp.

        Returns:
            web.json_response: Ответ с информацией о добавленной книге.
        """

    data = await request.json()
    book = Book(**data)
    db = request.app["db"]
    result = await add_book_to_db(db, book)
    return web.json_response(result)


# эндпоинт для удаления книги по айди
@token_required
async def delete_book(request):
    """Обработчик для удаления книги по ID.

        Удаляет книгу из базы данных по заданному идентификатору.
        Необходим токен доступа для выполнения этой операции.

        Args:
            request: Объект запроса Aiohttp.

        Returns:
            web.json_response: Ответ с статусом удаления или ошибка 404.
        """
    book_id = int(request.match_info["book_id"])
    db = request.app["db"]
    result = await delete_book_from_db(db, book_id)
    if result["status"] == "success":
        return web.json_response({"status": "Book deleted successfully"})
    else:
        raise web.HTTPNotFound(text="Book not found")


# эндпоинт для получения списка всех книг с пагинацией offset, limit
@token_required
async def get_books(request):
    """Обработчик для получения списка всех книг с поддержкой пагинации.

        Возвращает список книг из базы данных с параметрами offset и limit.
        Необходим токен доступа для выполнения этой операции.

        Args:
            request: Объект запроса Aiohttp.

        Returns:
            web.json_response: Ответ с списком книг.
        """
    db = request.app["db"]
    offset = int(request.query.get("offset", 0))
    limit = int(request.query.get("limit", 10))
    books = await get_books_from_db(db, offset, limit)
    return web.json_response({"books": books})


def setup_routes(app):
    """Настройка маршрутов для приложения Aiohttp.

        Args:
            app: Объект приложения Aiohttp.
        """
    app.router.add_post("/login", login)  # Эндпоинт для логина
    app.router.add_post("/books", add_book)  # Эндпоинт для добавления книги
    app.router.add_delete("/books/{book_id}", delete_book)  # Эндпоинт для удаления книги
    app.router.add_get("/books", get_books)  # Эндпоинт для получения списка книг
