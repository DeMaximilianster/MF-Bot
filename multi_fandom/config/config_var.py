# -*- coding: utf-8 -*-
from multi_fandom.config.config_func import *

# Список всех МФ2-чатов, кроме Админосостава и Комитета
global_database = Database()
chat_list = global_database.get_all('Главный чат')
chat_list += global_database.get_all('Подчат')
chat_list += global_database.get_all('Игровая')
chat_list += global_database.get_all('Ролевая')

# Список всех МФ2-чатов
# TODO тут слишком много строк, попробовать пофиксить
full_chat_list = global_database.get_all('Главный чат')
full_chat_list += global_database.get_all('Подчат')
full_chat_list += global_database.get_all('Игровая')
full_chat_list += global_database.get_all('Ролевая')
full_chat_list += global_database.get_all('Админосостав')
full_chat_list += global_database.get_all('Комитет')
del global_database

# Клавиатура для вопроса, иронично ли признание оскорбления/провокации
ironic_keyboard = telebot.types.InlineKeyboardMarkup()
ironic_keyboard.add(telebot.types.InlineKeyboardButton("Да", callback_data="ironic"))
ironic_keyboard.add(telebot.types.InlineKeyboardButton("Нет", callback_data="non_ironic"))
ironic_keyboard.row_width = 1

# Клавиатура для голосовашек
vote_keyboard = telebot.types.InlineKeyboardMarkup()
vote_keyboard.add(telebot.types.InlineKeyboardButton("За", callback_data="favor"))
vote_keyboard.add(telebot.types.InlineKeyboardButton("Против", callback_data="against"))
vote_keyboard.add(telebot.types.InlineKeyboardButton("Воздерживаюсь", callback_data="abstain"))
vote_keyboard.row_width = 1

# Тестовая клавиатура, кнопки не нажимаются
test_keyboard = telebot.types.InlineKeyboardMarkup()
test_keyboard.add(telebot.types.InlineKeyboardButton("Тестовая кнопка 1", callback_data="1"))
test_keyboard.add(telebot.types.InlineKeyboardButton("Тестовая кнопка 2", callback_data="2"))
test_keyboard.add(telebot.types.InlineKeyboardButton("Тестовая кнопка 3", callback_data="3"))
test_keyboard.row_width = 1

# Клавиатура для выбора, куда постить голосовашку
where_keyboard = telebot.types.InlineKeyboardMarkup()
where_keyboard.add(telebot.types.InlineKeyboardButton("Сюда", callback_data="here"))
where_keyboard.add(telebot.types.InlineKeyboardButton("В канал голосовашек", callback_data="there"))
where_keyboard.row_width = 1

# Клавиатура для выбора, куда постить мульти-голосовашку
m_where_keyboard = telebot.types.InlineKeyboardMarkup()
m_where_keyboard.add(telebot.types.InlineKeyboardButton("Сюда", callback_data="m_here"))
m_where_keyboard.add(telebot.types.InlineKeyboardButton("В канал голосовашек", callback_data="m_there"))
m_where_keyboard.row_width = 1

# Клавиатура для выбора, куда постить адапт-голосовашку
a_where_keyboard = telebot.types.InlineKeyboardMarkup()
a_where_keyboard.add(telebot.types.InlineKeyboardButton("Сюда", callback_data="a_here"))
a_where_keyboard.add(telebot.types.InlineKeyboardButton("В канал голосовашек", callback_data="a_there"))
a_where_keyboard.row_width = 1

# Клавиатура для признания предложения для мульти-голосовашки адекватным/неадекватным
adequate_keyboard = telebot.types.InlineKeyboardMarkup()
adequate_keyboard.add(telebot.types.InlineKeyboardButton("Адекватно", callback_data="adequate"))
adequate_keyboard.add(telebot.types.InlineKeyboardButton("Неадекватно", callback_data="inadequate"))
adequate_keyboard.row_width = 1

# Клавиатура для признания предложения для адапт-голосовашки адекватным/неадекватным
a_adequate_keyboard = telebot.types.InlineKeyboardMarkup()
a_adequate_keyboard.add(telebot.types.InlineKeyboardButton("Адекватно", callback_data="a_adequate"))
a_adequate_keyboard.add(telebot.types.InlineKeyboardButton("Неадекватно", callback_data="inadequate"))
a_adequate_keyboard.row_width = 1
