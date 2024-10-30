import jwt
from aiohttp import web
from datetime import datetime, timezone, timedelta
from app.config import SECRET_KEY, ALGORITHM


def create_access_token(data: dict):
    """Создает токен доступа для пользователя.

        Токен содержит полезную нагрузку с данными пользователя и время
        истечения срока действия.

        Args:
            data (dict): Данные, которые нужно закодировать в токене.

        Returns:
            str: Закодированный JWT токен.
        """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def token_required(handler):
    """Декоратор, который защищает обработчики маршрутов.

        Проверяет наличие и валидность токена в заголовке запроса.
        Если токен отсутствует или недействителен, возвращает ошибку 401.

        Args:
            handler (callable): Обработчик маршрута, который нужно защитить.

        Returns:
            callable: Обернутый обработчик, который выполняет проверку токена.
        """

    def wrapper(request):
        token = request.headers.get("Authorization")
        if not token:
            raise web.HTTPUnauthorized(text="Missing authorization token")
        try:
            payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
            request["user"] = payload
        except jwt.ExpiredSignatureError:
            raise web.HTTPUnauthorized(text="Token expired")
        except jwt.InvalidTokenError:
            raise web.HTTPUnauthorized(text="Invalid token")

        return handler(request)

    return wrapper
