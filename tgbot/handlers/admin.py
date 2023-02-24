from aiogram import Dispatcher
from aiogram.types import Message

from ..misc import db

async def admin_start(message: Message):
    result = db.get_count_order_ready_for_admin(False)
    await message.answer(f"Привет админ, заказов в наличии: {str(result[0])} выбери что надо сделать")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
