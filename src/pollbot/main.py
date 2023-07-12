import logging

from aiogram import Bot, Dispatcher

from pollbot.config import get_config
from pollbot.deta_state_srorage import DetaStateStorage
from pollbot.handlers.basic_handlers import router as basic_router
from pollbot.handlers.errors_handler import router as errors_router
from pollbot.middleware import deta_middleware
from pollbot.middleware.logging_middleware import LoggingMiddleware
from pollbot.middleware.upd_dumper_middleware import UpdatesDumperMiddleware


def get_webhook_path(conf):
    return f"/bot/{conf.bot_token.get_secret_value()}"


def get_webhook_url(conf, webhook_path):
    return conf.deta_space_app_hostname + webhook_path


def setup_dispatcher():
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

    storage = DetaStateStorage(conf.deta_project_key.get_secret_value())
    dispatcher = Dispatcher(storage=storage, config=conf)

    dispatcher.update.outer_middleware(UpdatesDumperMiddleware(conf.deta_project_key.get_secret_value()))

    deta_mid = deta_middleware.DetaMiddleware(conf.deta_project_key.get_secret_value())
    dispatcher.message.middleware.register(deta_mid)
    dispatcher.callback_query.middleware.register(deta_mid)

    dispatcher.message.middleware.register(LoggingMiddleware())
    dispatcher.callback_query.middleware.register(LoggingMiddleware())

    dispatcher.include_router(basic_router)
    dispatcher.include_router(errors_router)

    return dispatcher, bot


def main():
    dispatcher, bot = setup_dispatcher()
    dispatcher.run_polling(bot)


if __name__ == '__main__':
    main()
