from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from .user import CommandBot
from ..misc import db
from ..keyboards import inline


class OrderCoffee(StatesGroup):
    waiting_drink_name_coffee = State()
    waiting_coffee_size = State() 
    waiting_coffee_descr = State() 
    waiting_coffee_ready = State()

async def drinks_coffee(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text not in inline.button_drink_select:
        await message.answer("Пожалуйста, выберите напиток, используя клавиатуру ниже.")
        return
    async with state.proxy() as data:
            data['user_id'] = int(message.from_user.id)
            data['order_type'] = message.text
    button_case_select_coffee = ReplyKeyboardMarkup(resize_keyboard=True)
    for coffee_select in db.get_stock_list():
        button_case_select_coffee.add(coffee_select[0])
    button_case_select_coffee.add(inline.button_cancel)
    await message.answer("Выберите кофе:", reply_markup=button_case_select_coffee)
    await state.set_state(OrderCoffee.waiting_drink_name_coffee)

async def drinks_coffee_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order_name'] = message.text
    if message.text.lower() == "Эспрессо":
        await message.answer("Выберите объём кофе:", reply_markup=inline.button_case_select_size_expresso)
    if message.text.lower() != "Эспрессо":
        await message.answer("Выберите объём кофе:", reply_markup=inline.button_case_select_size_coffee)
    await state.set_state(OrderCoffee.waiting_coffee_size)


async def drinks_coffee_size(message: types.Message, state: FSMContext):
    if message.text.lower() not in (inline.button_coffee_sizes + inline.button_expresso_sizes):
        await message.answer("Пожалуйста, выберите объём, используя клавиатуру ниже.")
        return
    async with state.proxy() as data:
            data['order_number'] = message.text
    await message.answer(f"Введите комментарий (что добавить, почему и зачем).\n"
                        "Нажмите 'Пропустить' чтобы пропустить", reply_markup=inline.button_case_skip_and_cancel)
    await OrderCoffee.next()

async def coffee_descr(message: types.Message, state: FSMContext):
    if message.text == "Пропустить":
        async with state.proxy() as data:
            data['order_descr'] = "Без комментариев"
    else:
        async with state.proxy() as data:
            data['order_descr'] = message.text
    user_data = await state.get_data()
    await message.answer(f"Вы заказали {user_data['order_type']}, {user_data['order_name']} объёмом {user_data['order_number']}.\n"
                         f"Нажмите готово, для подтверждения заказа", reply_markup=inline.button_case_ready_and_cancel)
    await OrderCoffee.next()
    
async def coffee_ready(message: types.Message, state: FSMContext):
    if message.text !="Готово":
        await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже.")
        return
    async with state.proxy() as data:
            data['order_ready'] = False
    print(data)
    if(not db.get_worker_working(True)):
        await message.answer("Не удалось совершить заказ!", reply_markup=inline.button_case_menu)
        await state.finish()
    else:
        await db.add_order(state)
        await state.finish()
        await message.answer("Ваш заказ принят", reply_markup=inline.button_case_menu)
        await CommandBot.bot.send_message(db.get_worker_working(True)[0], "Есть новый заказ!!!")

def register_handlers_drinks(dp: Dispatcher):
    dp.register_message_handler(drinks_coffee, Text(equals="Кофе", ignore_case=True), state="*")
    dp.register_message_handler(drinks_coffee_name, state=OrderCoffee.waiting_drink_name_coffee)
    dp.register_message_handler(drinks_coffee_size, state=OrderCoffee.waiting_coffee_size)
    dp.register_message_handler(coffee_descr, state=OrderCoffee.waiting_coffee_descr)
    dp.register_message_handler(coffee_ready, state=OrderCoffee.waiting_coffee_ready)