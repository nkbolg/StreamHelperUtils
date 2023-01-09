import asyncio

from aiogram import Bot
# from aiogram.types import BotCommandScopeAllChatAdministrators, BotCommand

from bot.pollbot.config import get_config
from bot.pollbot.main import get_webhook_url, get_webhook_path


async def main():
    conf = get_config()
    webhook_path = get_webhook_path(conf)
    webhook_url = get_webhook_url(conf, webhook_path)
    bot = Bot(token=conf.bot_token.get_secret_value())
    res = await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    print("Set webhook:", res)
    print(webhook_url)
    # res = await bot.set_my_commands(commands=[
    #     BotCommand(command="/create_poll", description="начать опрос")
    # ])
    # # , scope = BotCommandScopeAllChatAdministrators()
    # print(res)
    await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
