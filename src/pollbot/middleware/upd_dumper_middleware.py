from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import TelegramObject, Update
from deta import Deta


class UpdatesDumperMiddleware(BaseMiddleware):
    def __init__(self, deta_project_key: str):
        self.updates_db = Deta(deta_project_key).Base("updates_dump")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        json_event = event.json(exclude_none=True)
        key = str(event.update_id)
        self.updates_db.put(json_event, key=key)

        res = await handler(event, data)
        if res is UNHANDLED:
            self.updates_db.update({'unhandled': True}, key=key)
        return res
