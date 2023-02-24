from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from .user import CommandBot
from ..misc import db
from ..keyboards import inline

class OrderTea(StatesGroup):
    waiting_tea_descr = State()
    waiting_tea_ready = State()

async def drinks_tea(message: types.Message, state: FSMContext):
    print(message.text)
    if message.text not in inline.button_drink_select:
        await message.answer("Пожалуйста, выберите напиток, используя клавиатуру ниже.")
        return
    async with state.proxy() as data:
            data['user_id'] = int(message.from_user.id)
            data['order_type'] = "Напитки"
            data['order_name'] = message.text
            data['order_number'] = "350мл"
    await message.answer(f"Введите комментарий (что добавить, почему и зачем).\n"
                        "Нажмите 'Пропустить' чтобы пропустить", reply_markup=inline.button_case_skip_and_cancel)
    await OrderTea.next()
    
async def tea_descr(message: types.Message, state: FSMContext):
    if message.text == "Пропустить":
        async with state.proxy() as data:
            data['order_descr'] = "Без комментариев"
    else:
        async with state.proxy() as data:
            data['order_descr'] = message.text
    user_data = await state.get_data()
    await OrderTea.next()
    await message.answer(f"Вы хотите заказать {user_data['order_name']} объёмом {user_data['order_number']}.\n"
                         f"Нажмите готово, для подтверждения заказа", reply_markup=inline.button_case_ready_and_cancel)

async def tea_ready(message: types.Message, state: FSMContext):
    if message.text !="Готово":
        await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже.")
        return
    async with state.proxy() as data:
            data['order_ready'] = False
    print(data)
    if(not db.get_worker_working(True)):
        await message.answer("Не удалось совершить заказ", reply_markup=inline.button_case_menu)
        await state.finish()
    else:
        await db.add_order(state)
        await state.finish()
        await message.answer("Ваш заказ принят", reply_markup=inline.button_case_menu)
        await CommandBot.bot.send_message(db.get_worker_working(True)[0], "Есть новый заказ!!!")
    


def register_handlers_tea(dp: Dispatcher):
    dp.register_message_handler(drinks_tea, Text(equals="Чай", ignore_case=True), state="*")
    dp.register_message_handler(drinks_tea, Text(equals="Какао", ignore_case=True), state="*")
    dp.register_message_handler(tea_descr, state=OrderTea.waiting_tea_descr)
    dp.register_message_handler(tea_ready, state=OrderTea.waiting_tea_ready)