from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_to_registration = KeyboardButton('Регистрация')
button_to_work_open = KeyboardButton('Открыть смену')
button_to_work_close = KeyboardButton('Закрыть смену')

button_to_watch_order = KeyboardButton('Посмотреть заказы')

button_case_registration = ReplyKeyboardMarkup(resize_keyboard = True).add(button_to_registration)
button_case_work_open = ReplyKeyboardMarkup(resize_keyboard = True).add(button_to_work_open)

button_case_work_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(button_to_watch_order)\
    .add(button_to_work_close)
