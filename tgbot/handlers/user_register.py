from aiogram import Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from ..keyboards import inline
from ..misc import db

class FSMregister(StatesGroup):
    user_id = State()
    user_center = State()
    user_descr = State()
    user_name = State()

# Начало диалога регистрации пользователя
#@dp.message_handler(commands = 'Регистрация', state = None)
async def register_start(message: types.Message, state: FSMContext):
    if(not await db.user_exists(message.from_user.id)):
        await FSMregister.user_id.set()
        async with state.proxy() as data:
            data['user_id'] = int(message.from_user.id)
        await FSMregister.next()
        await message.answer("Здравствуй, это тест бота, этап регистрации. Выбери торговый центр (если вы находитесь в другом месте, введите название ТЦ или магазина на клавиатуре): ", reply_markup=inline.button_case_select_center)
    else:
        await message.answer("Вы уже зарегистрированы! ", reply_markup=inline.button_case_menu)
        return



# Ловим ответ и пишем в словарь
#@dp.message_handler(state = FSMregister.user_center)
async def load_center(message: types.Message, state: FSMContext):
    await FSMregister.user_center.set()
    async with state.proxy() as data:
        data['user_center'] = message.text
    await FSMregister.next()
    await message.reply("Хорошо, а теперь опиши по подробнее о месте куда доставлять кофе (Номер офиса, название магазина, этаж, как пройти и т.п.), постарайтесь более подробно описать местоположение", reply_markup=types.ReplyKeyboardRemove())
    
#@dp.message_handler(state = FSMregister.user_descr)
async def load_descr(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_descr'] = message.text
    await FSMregister.next()
    await message.reply("Отлично, а теперь введи имя, как к тебе обращаться", reply_markup=types.ReplyKeyboardRemove())

#@dp.message_handler(state = FSMregister.user_name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_name'] = message.text
    await db.add_user(state)
    await state.finish()
    await message.answer("Отлично, вы зарегистрированы! ", reply_markup=inline.button_case_menu)



def register_user_register(dp: Dispatcher):
    dp.register_message_handler(register_start, Text(equals="Регистрация", ignore_case=True), state = None)
    dp.register_message_handler(load_center, state = FSMregister.user_center)
    dp.register_message_handler(load_descr, state = FSMregister.user_descr)
    dp.register_message_handler(load_name, state = FSMregister.user_name)