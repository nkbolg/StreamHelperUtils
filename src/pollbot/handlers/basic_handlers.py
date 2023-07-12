import random
from typing import Callable, Dict, Any, Awaitable

from aiogram.enums import ParseMode, ChatType

from pollbot.data import artists as static_artists

import aiogram.exceptions
from aiogram import BaseMiddleware, Bot
from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessage
from aiogram.types import TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

kbd = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Завершить", callback_data="finish"),
     InlineKeyboardButton(text="Повторить", callback_data="new")]
])


class UserRegMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any],
    ) -> Any:
        users_db = data["users_db"]
        current_username = event.from_user.username
        current_id = event.from_user.id
        full_name = event.from_user.full_name
        users_db.reg_user(id_=current_id, name=full_name, username=current_username)
        return await handler(event, data)


class DataLoaderMiddleware(BaseMiddleware):
    def __init__(self):
        self.artists = static_artists

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data['artists'] = self.artists
        return await handler(event, data)


router.message.middleware.register(UserRegMiddleware())
router.message.middleware.register(DataLoaderMiddleware())
router.callback_query.middleware.register(DataLoaderMiddleware())


@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start_handler(
        message: types.Message):
    await message.answer('Напиши исполнителя, которого ты хочешь добавить в плейлист🤟')


@router.message(F.from_user.id == 99988303, F.text == 'погнали', F.chat.type != ChatType.PRIVATE)
async def start_poll(message: types.Message, state: FSMContext, artists: list[str]):
    await message.delete()
    await send_new_post(message, state, artists)


@router.message(F.chat.type == ChatType.PRIVATE)
async def text_handler(message: types.Message, bot: Bot):
    await message.answer("Предложение отправлено")
    await message.forward(99988303)
    ref = message.from_user.mention_markdown()
    await bot.send_message(99988303, ref, parse_mode=ParseMode.MARKDOWN_V2)


async def send_new_post(message: types.Message, state: FSMContext, artists: list[str]):
    artists = random.sample(artists, 5)
    msg = await message.answer_poll("Что дальше?", artists, allows_multiple_answers=True, reply_markup=kbd)
    await state.update_data(poll_id=msg.message_id)


@router.callback_query(F.from_user.id == 99988303)
async def query_handler(query: types.CallbackQuery, bot: aiogram.Bot, state: FSMContext, artists: list[str]):
    chat_id = query.message.chat.id
    data = await state.get_data()
    poll_msg_id = data['poll_id']
    if query.data == "new":
        await send_new_post(query.message, state, artists)
        return DeleteMessage(
            chat_id=chat_id,
            message_id=poll_msg_id,
        )
    elif query.data == "finish":
        await bot.stop_poll(chat_id, poll_msg_id, reply_markup=kbd)
