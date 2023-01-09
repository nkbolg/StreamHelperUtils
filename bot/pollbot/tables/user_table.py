# noinspection PyProtectedMember
from deta.base import _Base as BaseType


class UsersTable:
    def __init__(self, base: BaseType):
        self.base = base

    def reg_user(self, id_: int, name: str, username: str):
        userdata = {
            'id': id_,
            'name': name,
            'telegram_username': username,
            'phone': None,
            'mailing_idx': 0
        }
        self.base.put(key=str(id_), data=userdata)

    def update_phone(self, id_: int, phone: str):
        key = str(id_)
        data = self.base.get(key)
        data['phone'] = phone
        self.base.put(key=key, data=data)
