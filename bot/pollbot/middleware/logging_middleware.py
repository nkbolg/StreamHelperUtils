import functools
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        try:
            print(f"calling {self._get_name(handler)}")
        finally:
            res = await handler(event, data)

        print(f"success")
        return res

    def _get_name(self, handler):
        while isinstance(handler, functools.partial):
            handler = handler.args[0]

        name = handler.__wrapped__.__self__.callback.__name__
        return name
