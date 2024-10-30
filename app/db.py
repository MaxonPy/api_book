import asyncpg
from app.config import DATABASE_URL
from app.models import Book


# Функция для инициализации пула соединений
async def init_db():
    """Инициализирует пул соединений с базой данных.

    Returns:
        asyncpg.pool.Pool: Пул соединений к базе данных.
    """
    return await asyncpg.create_pool(DATABASE_URL)  # Возвращаем пул соединений


# Функция для добавления книги в базу данных
async def add_book_to_db(pool, book: Book):
    """Добавляет книгу в базу данных.

        Args:
            pool (asyncpg.pool.Pool): Пул соединений к базе данных.
            book (Book): Объект книги, который нужно добавить.

        Returns:
            dict: Словарь с информацией о добавленной книге.
        """

    async with pool.acquire() as conn:  # Получаем соединение из пула
        result = await conn.fetchrow(
            "INSERT INTO books (title, author, year, isbn) VALUES ($1, $2, $3, $4) RETURNING *",
            book.title, book.author, book.year, book.isbn
        )
        return dict(result)  # Возвращаем результат как словарь


# Функция для удаления книги по ID
async def delete_book_from_db(pool, book_id: int):
    """Удаляет книгу из базы данных по её ID.

        Args:
            pool (asyncpg.pool.Pool): Пул соединений к базе данных.
            book_id (int): ID книги, которую нужно удалить.

        Returns:
            dict: Статус операции удаления.
        """

    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM books WHERE id = $1", book_id)
        return {"status": "success" if result == "DELETE 1" else "not_found"}


# Функция для получения всех книг с поддержкой пагинации
async def get_books_from_db(pool, offset: int = 0, limit: int = 10):
    """Получает все книги из базы данных с поддержкой пагинации.

        Args:
            pool (asyncpg.pool.Pool): Пул соединений к базе данных.
            offset (int): Количество записей, которые нужно пропустить (по умолчанию 0).
            limit (int): Максимальное количество возвращаемых записей (по умолчанию 10).

        Returns:
            list: Список словарей, содержащих информацию о книгах.
        """

    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM books OFFSET $1 LIMIT $2", offset, limit)
        return [dict(row) for row in rows]