import logging

from aiogram import Bot, Dispatcher
from deta import Deta
from fastapi import FastAPI

from .config import get_config
from .deta_state_srorage import DetaStateStorage
from .handlers.basic_handlers import router as basic_router
from .handlers.errors_handler import router as errors_router
from .middleware import deta_middleware
from .middleware.logging_middleware import LoggingMiddleware
from .tables.user_table import UsersTable


def get_webhook_path(conf):
    return f"/bot/{conf.bot_token.get_secret_value()}"


def get_webhook_url(conf, webhook_path):
    return conf.base_url + webhook_path


def setup_app():
    """Точка входа в приложение"""

    # включение логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: "
               "%(filename)s: "
               "%(levelname)s: "
               "%(funcName)s(): "
               "%(lineno)d:\t"
               "%(message)s",
    )

    # получение класса хранящего конфигурируемые параметры
    conf = get_config()

    # создание и запуск объекта бота
    bot = Bot(token=conf.bot_token.get_secret_value())

    storage = DetaStateStorage(conf.deta_project_key.get_secret_value(), conf.db_prefix)
    dispatcher = Dispatcher(storage=storage, config=conf)

    deta_mid = deta_middleware.DetaMiddleware(conf.deta_project_key.get_secret_value())
    dispatcher.message.middleware.register(deta_mid)
    dispatcher.callback_query.middleware.register(deta_mid)

    dispatcher.message.middleware.register(LoggingMiddleware())
    dispatcher.callback_query.middleware.register(LoggingMiddleware())

    dispatcher.include_router(basic_router)
    dispatcher.include_router(errors_router)

    app = FastAPI()

    webhook_path = get_webhook_path(conf)
    webhook_url = get_webhook_url(conf, webhook_path)

    @app.post(webhook_path)
    async def bot_webhook(update: dict):
        res = await dispatcher.feed_webhook_update(bot, update)
        return res

    @app.get(f"/{conf.bot_token.get_secret_value()}")
    async def setup():
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != webhook_url:
            await bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True
            )
            return "Updated"
        return "Up to date"

    return app
