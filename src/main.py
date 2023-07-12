from fastapi import FastAPI

from pollbot.config import get_config
from pollbot.main import setup_dispatcher


def get_webhook_path(conf):
    return f"/bot/{conf.bot_token.get_secret_value()}"


def get_webhook_url(conf, webhook_path):
    return conf.deta_space_app_hostname + webhook_path


def setup_app():
    app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
    conf = get_config()

    webhook_path = get_webhook_path(conf)
    webhook_url = get_webhook_url(conf, webhook_path)

    dispatcher, bot = setup_dispatcher()

    @app.post(webhook_path)
    async def bot_webhook(update: dict):
        res = await dispatcher.feed_webhook_update(bot, update)
        return res

    @app.get("/bot/update_webhook")
    async def setup():
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        return "Updated"

    return app


app = setup_app()
