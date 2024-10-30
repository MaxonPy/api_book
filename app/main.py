from aiohttp import web
from app.routes import setup_routes
from app.db import init_db
from aiohttp_swagger import setup_swagger


async def create_app():
    app = web.Application()
    app["db"] = await init_db()  # сохраняем пул соединений в app
    setup_routes(app)  # настройка маршрутов
    setup_swagger(app, swagger_url="/swagger", ui_version=3)
    return app

if __name__ == "__main__":
    web.run_app(create_app())
