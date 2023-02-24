from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
##from ..misc import db

buttons_registration = ["Регистрация"]

# Кнопки главного меню
button_to_order = KeyboardButton('Заказать напитки')
button_profile = KeyboardButton('Посмотреть профиль')
button_edit_profile = KeyboardButton('Изменить профиль')
button_view_status = KeyboardButton('Узнать статус')

# Кнопки редактирования профиля
button_edit_name = KeyboardButton('Изменить имя')
button_edit_center = KeyboardButton('Изменить торговый центр')
button_edit_descr = KeyboardButton('Изменить описание')

# Кнопки напитков

button_drink_select = ["Чай", "Кофе", "Какао"]

buttons_center = ["Звёздный", "Северный"]

button_coffee_sizes = ["250мл", "350мл", "450мл"]
button_expresso_sizes = ["30мл", "60мл"]


# Кнопка "готово" в заказах
button_ready = KeyboardButton('Готово')
button_skip = KeyboardButton('Пропустить')
button_ready_and_cancel = ["Готово", "Отмена"]

# Кнопка отмены действия
button_cancel = KeyboardButton('Отмена')

# Кнопки Главное меню и о боте
button_menu = KeyboardButton('Главное меню')
button_bot = KeyboardButton('О боте...')

button_case_registration = ReplyKeyboardMarkup(resize_keyboard = True).add(buttons_registration)


# Кейс главного меню
button_case_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(button_to_order)\
    .add(button_profile)\
        .add(button_edit_profile)\
            .add(button_view_status)

# Кейс редактирования профиля
button_case_edit_profile = ReplyKeyboardMarkup(resize_keyboard = True).add(button_edit_name)\
    .add(button_edit_center)\
        .add(button_edit_descr)\
            .add(button_cancel)

# Кейс выбора напитков
button_case_select_drink = ReplyKeyboardMarkup(resize_keyboard=True)
for drink_select in button_drink_select:
    button_case_select_drink.add(drink_select)
button_case_select_drink.add(button_cancel)

# Кейс выбор кофе


# Кейс выбора объема кофе
button_case_select_size_coffee = ReplyKeyboardMarkup(resize_keyboard=True)
for coffee_size in button_coffee_sizes:
    button_case_select_size_coffee.add(coffee_size)
button_case_select_size_coffee.add(button_cancel)
button_case_select_size_expresso = ReplyKeyboardMarkup(resize_keyboard=True)
for coffee_expresso_size in button_expresso_sizes:
    button_case_select_size_expresso.add(coffee_expresso_size)
button_case_select_size_expresso.add(button_cancel)


# Кейс кнопок отмена и готово
button_case_ready_and_cancel = ReplyKeyboardMarkup(resize_keyboard = True)
for ready_and_cancel in button_ready_and_cancel:
    button_case_ready_and_cancel.add(ready_and_cancel)

# Кейс кнопок пропустить и отмена
button_case_skip_and_cancel = ReplyKeyboardMarkup(resize_keyboard = True).add(button_skip)\
    .add(button_cancel)

# Кейс выбора торгового центра
button_case_select_center = ReplyKeyboardMarkup(resize_keyboard=True)
for center_select in buttons_center:
    button_case_select_center.add(center_select)
button_case_select_center.add(button_cancel)

# Кейс о статусе бота
button_case_bot = ReplyKeyboardMarkup(resize_keyboard = True).add(button_menu)\
    .add(button_bot)