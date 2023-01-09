from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from deta import Deta

from ..tables.user_table import UsersTable


class DetaMiddleware(BaseMiddleware):
    def __init__(self, deta_project_key: str):
        deta = Deta(deta_project_key)
        self.users_db = UsersTable(deta.Base('user_data'))

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data['users_db'] = self.users_db
        return await handler(event, data)
