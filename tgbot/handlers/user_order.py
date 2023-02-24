
from aiogram import Dispatcher, types

from aiogram.utils.exceptions import MessageNotModified
from aiogram.utils.callback_data import CallbackData

from ..misc import db
from ..keyboards import inline
from .user import CommandBot

from contextlib import suppress

user_data = {}
count = {}
callback_numbers = CallbackData("fabnum", "action")


def get_keyboard_fab():
    buttons = [
        types.InlineKeyboardButton(text="<--", callback_data=callback_numbers.new(action="back")),
        types.InlineKeyboardButton(text=f"{count['number']}/{page[0]}", callback_data=callback_numbers.new(action="back")),
        types.InlineKeyboardButton(text="-->", callback_data=callback_numbers.new(action="next")),
        types.InlineKeyboardButton(text="Отменить заказ", callback_data=callback_numbers.new(action="delete"))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard


async def update_num_text(message: types.Message, user_id: int, new_value: int):
    with suppress(MessageNotModified):
        result = db.get_order(user_id, False, new_value, 1)
        await message.edit_text(f"Ваш заказ № {result[0]}\n\
    Тип заказа: {result[1]}, {result[2]}\n\
    Объем: {result[3]}\n\
    Комментарий к заказу:\n\
    {result[4]}", reply_markup=get_keyboard_fab())


async def get_for_user_order(message: types.Message):
    if (not await db.user_order_exists(message.from_user.id, False)):
        await message.answer("У вас нет заказов!", reply_markup=inline.button_case_menu)
        return
    global page
    page = db.get_count_order_ready(message.from_user.id, False)
    count['number'] = 1
    user_data[message.from_user.id] = 0
    result = db.get_order(message.from_user.id, False, 0, 1)
    await message.answer(f"Ваш заказ № {result[0]}\n\
Тип заказа: {result[1]}, {result[2]}\n\
Объем: {result[3]}\n\
Комментарий к заказу:\n\
{result[4]}", reply_markup=get_keyboard_fab())



async def callbacks_page_order(call: types.CallbackQuery, callback_data: dict):
    user_value = user_data.get(call.from_user.id, 0)
    action = callback_data["action"]
    user_id = call.from_user.id

    if action == "next":
        if page[0] == 1 or page[0] == count['number']:
            await call.answer()
        else:
            count['number'] = count['number'] + 1
            user_data[call.from_user.id] = user_value + 1
            await update_num_text(call.message, user_id, user_value+1)
        
    elif action == "back":
        if count['number'] == 1:
            await call.answer()
        else:
            count['number'] = count['number'] - 1
            user_data[call.from_user.id] = user_value - 1
            await update_num_text(call.message, user_id, user_value-1)

    await call.answer()

# @dp.callback_query_handler(callback_numbers.filter(action=["finish"]))
async def callbacks_num_finish_fab(call: types.CallbackQuery):
    user_value = user_data.get(call.from_user.id, 0)
    result = db.get_order(call.from_user.id, False, user_value, 1)
    db.delete(result[0])
    await call.message.edit_text(f"заказ № {result[0]}, успешно отменен!")
    await CommandBot.bot.send_message(db.get_worker_working(True)[0], f"Заказ № {result[0]}, ОТМЕНИЛИ!!!")
    await call.answer()

def register_user_order(dp: Dispatcher):
    dp.register_message_handler(get_for_user_order, commands="basket", state="*")
    dp.register_callback_query_handler(callbacks_page_order, callback_numbers.filter(action=["next", "back"]))
    dp.register_callback_query_handler(callbacks_num_finish_fab, callback_numbers.filter(action=["delete"]))
