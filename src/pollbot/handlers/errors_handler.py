import logging

from aiogram import Router
from aiogram.types.error_event import ErrorEvent

router = Router()


@router.errors()
async def error_handler(exception: ErrorEvent):
    print("Handled exception:", exception)
    logging.exception(exception.update)
