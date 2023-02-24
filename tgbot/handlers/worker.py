from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from tgbot.config import load_config

from aiogram.utils.exceptions import MessageNotModified
from aiogram.utils.callback_data import CallbackData
from contextlib import suppress

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from ..keyboards import worker_keyboard
from ..misc import db

config = load_config(".env")
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

class WorkerName(StatesGroup):
    waiting_for_working_name = State()

class OrderMessageReply(StatesGroup):
    waiting_for_new_message = State()

async def worker_start(message: Message):
    result = db.get_count_order_ready_for_admin(False)
    if (not await db.worker_exists(message.from_user.id)):
        await message.answer(f"Для начала зарегистрируйся", reply_markup=worker_keyboard.button_case_registration)
    elif (not await db.working_exists(True)):
        await message.answer(f"Откройте смену ", reply_markup=worker_keyboard.button_case_work_open)
    elif db.get_status_exists(message.from_user.id)[0] == False:
        await message.answer(f"Смена уже открыта, не вами!!", reply_markup=worker_keyboard.button_case_work_open)
    else:
        await message.answer(f"Смена открыта, заказов в наличии: {str(result[0])} ", reply_markup=worker_keyboard.button_case_work_menu)
        

# --------
# Регистрация продавца в БД
async def worker_registration(message: Message, state: FSMContext):
    if (not await db.worker_exists(message.from_user.id)):
        await message.answer(f"Введи своё отображаемое имя: ", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(WorkerName.waiting_for_working_name.state)
    else:
        await message.answer(f"Вы зарегистрированы", reply_markup=types.ReplyKeyboardRemove())
        return

async def worker_name(message: Message, state: FSMContext):
    db.add_worker(message.from_user.id, message.text)
    await state.finish()
    await message.answer("Регистрация прошла успешно", reply_markup=types.ReplyKeyboardRemove())
# --------


# --------
# Открытие смены
async def worker_status_open(message: Message):
    if db.get_status_exists(message.from_user.id)[0] == True:
        await message.answer(f"Смена уже открыта", reply_markup=worker_keyboard.button_case_work_menu)
        return
    else:
        db.set_edit_worker_status(True, message.from_user.id)
        await message.answer(f"Смена успешно открыта!!", reply_markup=worker_keyboard.button_case_work_menu)
#--------

# --------
# Закрытие
async def worker_status_close(message: Message):
    if db.get_status_exists(message.from_user.id)[0] == False:
        await message.answer(f"Смена уже закрыта", reply_markup=worker_keyboard.button_case_work_open)
        return
    else:
        db.set_edit_worker_status(False, message.from_user.id)
        await message.answer(f"Смена успешно закрыта!!", reply_markup=worker_keyboard.button_case_work_open)
#--------

#--------
# Просмотр ожидающих заказов
user_data = {}
count = {}
callback_numbers = CallbackData("fabnum", "action")


def get_keyboard_fab():
    buttons = [
        types.InlineKeyboardButton(text="<--", callback_data=callback_numbers.new(action="back")),
        types.InlineKeyboardButton(text=f"{count['number']}/{page[0]}", callback_data=callback_numbers.new(action="back")),
        types.InlineKeyboardButton(text="-->", callback_data=callback_numbers.new(action="next")),
        types.InlineKeyboardButton(text="Заказ выполнен", callback_data=callback_numbers.new(action="complete")),
        types.InlineKeyboardButton(text="Ответить заказчику", callback_data=callback_numbers.new(action="reply")),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard

def get_keyboard_yes_or_no():
    buttons = [
        types.InlineKeyboardButton(text="Да", callback_data=callback_numbers.new(action="yes")),
        types.InlineKeyboardButton(text="Нет", callback_data=callback_numbers.new(action="no")),
        types.InlineKeyboardButton(text="Ответить заказчику", callback_data=callback_numbers.new(action="reply")),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard

async def update_num_text(message: types.Message, new_value: int):
    with suppress(MessageNotModified):
        result = db.get_all_order(False, new_value, 1)
        user_view = db.get_user_info(result[1])
        await message.edit_text(f"Заказ № {result[0]}\n\
Тип заказа: {result[2]}, {result[3]}\n\
Объем: {result[4]}\n\
Комментарий к заказу:\n\
{result[5]}\n\
Дата заказа: {result[6]}\n\
Заказчик: {user_view}", reply_markup=get_keyboard_fab())


async def get_for_watch_user_order(message: types.Message):
    if db.get_count_order_ready_for_admin(False)[0] == 0:
        await message.answer("Заказов не обнаружено", reply_markup=worker_keyboard.button_case_work_menu)
        return
    print(db.get_count_order_ready_for_admin(False))
    global page
    page = db.get_count_all_order_ready(False)
    count['number'] = 1
    user_data[message.from_user.id] = 0
    result = db.get_all_order(False, 0, 1)
    user_view = db.get_user_info(result[1])
    await message.answer(f"Заказ № {result[0]}\n\
Тип заказа: {result[2]}, {result[3]}\n\
Объем: {result[4]}\n\
Комментарий к заказу:\n\
{result[5]}\n\
Дата заказа: {result[6]}\n\
Заказчик: {user_view}", reply_markup=get_keyboard_fab())



async def callbacks_page_order(call: types.CallbackQuery, callback_data: dict):
    user_value = user_data.get(call.from_user.id, 0)
    action = callback_data["action"]

    if action == "next":
        if page[0] == 1 or page[0] == count['number']:
            await call.answer()
        else:
            count['number'] = count['number'] + 1
            user_data[call.from_user.id] = user_value + 1
            await update_num_text(call.message, user_value+1)
        
    elif action == "back":
        if count['number'] == 1:
            await call.answer()
        else:
            count['number'] = count['number'] - 1
            user_data[call.from_user.id] = user_value - 1
            await update_num_text(call.message, user_value-1)

    await call.answer()


async def callbacks_set_complete_order(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user_value = user_data.get(call.from_user.id, 0)
    result = db.get_all_order(False, user_value, 1)
    action = callback_data["action"]

    if action == "complete":
        await call.message.edit_text(f"Вы уверены, что хотите завершить заказ № {result[0]}?", reply_markup=get_keyboard_yes_or_no())
        await call.answer()
   
    elif action == "yes":
        db.set_new_order_status(True, result[0])
        await call.message.edit_text(f"заказ № {result[0]}, успешно выполнен!")
        await state.finish()
        await call.answer()
        
    elif action == "no":
        await call.message.edit_text("Ок!")
        await state.finish()
        await call.answer()

    elif action == "reply":
        await call.message.edit_text("Напишите, что вы хотите написать заказчику:")
        await state.set_state(OrderMessageReply.waiting_for_new_message)
        await call.answer()

    await call.answer()

async def new_message_text(message: Message, state: FSMContext):
    user_value = user_data.get(message.from_user.id, 0)
    result = db.get_all_order(False, user_value, 1)
    await bot.send_message(result[1], message.text)
    await state.finish()
    await message.answer("Сообщение успешно отправлено", reply_markup=worker_keyboard.button_case_work_menu)
#


def register_worker(dp: Dispatcher):
    dp.register_message_handler(worker_start, commands=["start"], state="*", is_worker=True)
    dp.register_message_handler(worker_registration, Text(equals="Регистрация", ignore_case=True), state="*", is_worker=True)
    dp.register_message_handler(worker_name, state=WorkerName.waiting_for_working_name)

    dp.register_message_handler(get_for_watch_user_order, Text(equals="Посмотреть заказы", ignore_case=True), state="*", is_worker=True)
    dp.register_callback_query_handler(callbacks_page_order, callback_numbers.filter(action=["next", "back"]), is_worker=True)
    dp.register_callback_query_handler(callbacks_set_complete_order, callback_numbers.filter(action=["complete", "yes", "no", "reply"]), is_worker=True)
    dp.register_message_handler(new_message_text, state=OrderMessageReply.waiting_for_new_message)
    
    dp.register_message_handler(worker_status_open, Text(equals="Открыть смену", ignore_case=True), state="*", is_worker=True)
    dp.register_message_handler(worker_status_close, Text(equals="Закрыть смену", ignore_case=True), state="*", is_worker=True)
