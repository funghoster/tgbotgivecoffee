from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


from tgbot.config import load_config

from ..misc import db
from ..keyboards import inline

class CommandBot:
    config = load_config(".env")
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

class NewName(StatesGroup):
    waiting_for_new_name = State()
class NewCenter(StatesGroup):
    waiting_for_new_center = State()
class NewDescr(StatesGroup):
    waiting_for_new_descr = State()

async def user_start(message: types.Message):
    if(not await db.user_exists(message.from_user.id)):
        await message.answer("Пожалуйста зарегистрируйтесь", reply_markup=inline.button_case_registration)
        return
    await message.answer("Привет, выбери, что ты хочешь сделать. Введи \"Узнать статус\", чтобы узнать о статусе работы и о том, кто сейчас на точке", reply_markup=inline.button_case_menu)

async def drinks_start(message: types.Message,):
    if(not await db.user_exists(message.from_user.id)):
        await message.answer("Пожалуйста зарегистрируйтесь", reply_markup=inline.button_case_registration)
        return
    if(not db.get_worker_working(True)):
        
        await message.answer("На данный момент, ни кто не работает!", reply_markup=inline.button_case_menu)
        return
    await message.answer("Выберите напиток:", reply_markup=inline.button_case_select_drink)

async def user_profile(message: types.Message,):
    if(not await db.user_exists(message.from_user.id)):
        await message.answer("Пожалуйста зарегистрируйтесь", reply_markup=inline.button_case_registration)
        return
    record = db.get_user_info(message.from_user.id)
    await message.answer(f"Ваш профиль:\n"
                        f"👤Имя: {record[2]}\n"
                        f"🏠ТЦ: {record[0]}\n"
                        f"📝Описание: {record[1]}\n"
                        f"🗓Дата регистрации: {str(record[3])}\n"
                        f"Для изменения профиля введите команду \"/editprofile\" или выберите ниже", reply_markup=inline.button_case_menu)

async def user_edit_profile(message: types.Message,):
    await message.answer("Выберите что что хотите изменить:", reply_markup=inline.button_case_edit_profile)

# Фунция изменения имени пользователя
async def edit_name(message: types.Message, state: FSMContext):
    await message.answer("Введите имя: ", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(NewName.waiting_for_new_name.state)
 
async def set_new_name(message: types.Message, state: FSMContext):
    db.add_record_name(message.text, message.from_user.id)
    await message.answer("Сделано", reply_markup=inline.button_case_menu)
    await state.finish()
#------
# Фунция изменения торгового центра пользователя
async def edit_center(message: types.Message, state: FSMContext):
    await message.answer("Выбери торговый центр: ", reply_markup=inline.button_case_select_center)
    await state.set_state(NewCenter.waiting_for_new_center.state)
 
async def set_new_center(message: types.Message, state: FSMContext):
    db.add_record_center(message.text, message.from_user.id)
    await message.answer("Сделано", reply_markup=inline.button_case_menu)
    await state.finish()
#------
# Фунция изменения информации о пользователе
async def edit_info(message: types.Message, state: FSMContext):
    await message.answer("Введите информацию о себе: ", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(NewDescr.waiting_for_new_descr.state)
 
async def set_new_info(message: types.Message, state: FSMContext):
    db.add_record_description(message.text, message.from_user.id)
    await message.answer("Сделано", reply_markup=inline.button_case_menu)
    await state.finish()
#------





async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=inline.button_case_menu)

    
def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start", "menu"], state="*")
    dp.register_message_handler(user_start, Text(equals="Главное меню", ignore_case=True), state="*")
    dp.register_message_handler(drinks_start, commands="neworder", state="*")
    dp.register_message_handler(drinks_start, Text(equals="Заказать напитки", ignore_case=True), state="*")
    dp.register_message_handler(user_profile, Text(equals="Посмотреть профиль", ignore_case=True), state="*")
    dp.register_message_handler(user_edit_profile, commands="editprofile", state="*")
    dp.register_message_handler(user_edit_profile, Text(equals="Изменить профиль", ignore_case=True), state="*")
    dp.register_message_handler(edit_name, Text(equals="Изменить имя", ignore_case=True), state="*")
    dp.register_message_handler(set_new_name, state=NewName.waiting_for_new_name)
    dp.register_message_handler(edit_info, Text(equals="Изменить описание", ignore_case=True), state="*")
    dp.register_message_handler(set_new_info, state=NewDescr.waiting_for_new_descr)
    dp.register_message_handler(edit_center, Text(equals="Изменить торговый центр", ignore_case=True), state="*")
    dp.register_message_handler(set_new_center, state=NewCenter.waiting_for_new_center)
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")