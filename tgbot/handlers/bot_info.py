from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from ..misc import db
from ..keyboards import inline

async def work_status(message: types.Message,):
    result = db.get_worker_working(True)
    if(not result):
        await message.answer("На данный момент, на кофейном островке ни кого, нет", reply_markup=inline.button_case_menu)
    else:
        await message.answer(f"На данный момент работает: \n{result[1]}", reply_markup=inline.button_case_bot)


async def bot_info(message: types.Message,):
    await message.answer("Это альфа версия бота и он полностью создан одним из работников кофейни\n\
👉Вы так же можете помочь в его продвижении или просто оставить на чай:):\n\
👉Номер для переводов: +79094011608\n\
👉QIWI или Сбербанк", reply_markup=inline.button_case_menu)


def register_bot_info(dp: Dispatcher):
    dp.register_message_handler(work_status, Text(equals="Узнать статус", ignore_case=True), state="*")
    dp.register_message_handler(bot_info, Text(equals="О боте...", ignore_case=True), state="*")