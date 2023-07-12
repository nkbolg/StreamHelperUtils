from typing import Dict, Any, Optional, cast

from aiogram import Bot
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType

from deta import Deta


class DetaStateStorage(BaseStorage):
    def __init__(self, deta_project_key: str):
        self.deta_project_key = deta_project_key
        self.deta = Deta(self.deta_project_key)
        self.state_db = self.deta.Base(f'aiogram_state')
        self.data_db = self.deta.Base(f'aiogram_data')

    async def set_state(self, bot: Bot, key: StorageKey, state: StateType = None) -> None:
        value = cast(str, state.state if isinstance(state, State) else state)
        key = str(key.user_id)
        self.state_db.put(data=value, key=key)

    async def get_state(self, bot: Bot, key: StorageKey) -> Optional[str]:
        key = str(key.user_id)
        data = self.state_db.get(key)
        if data is None:
            return
        value = data['value']
        return cast(Optional[str], value)

    async def set_data(self, bot: Bot, key: StorageKey, data: Dict[str, Any]) -> None:
        key = str(key.user_id)
        self.data_db.put(data=data, key=key)

    async def get_data(self, bot: Bot, key: StorageKey) -> Dict[str, Any]:
        key = str(key.user_id)
        return self.data_db.get(key) or {}

    async def close(self) -> None:
        pass
