# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

bot_id = 575704111

# Список всех МФ2-чатов, кроме Админосостава и Комитета
global_database = Database()

admin_place = global_database.get('chats', ('purpose', "Админосостав"))[0]

chat_list = global_database.get_many('Главный чат')
chat_list += global_database.get_many('Подчат')
chat_list += global_database.get_many('Игровая')
chat_list += global_database.get_many('Ролевая')

# Список всех МФ2-чатов
full_chat_list = global_database.get_all('chats')

# Список всех МФ2-каналов
channel_list = global_database.get_all('channels')
del global_database

# Клавиатура для вопроса, иронично ли признание оскорбления/провокации
ironic_keyboard = InlineKeyboardMarkup()
ironic_keyboard.add(InlineKeyboardButton("Иронично", callback_data="ironic"))
ironic_keyboard.add(InlineKeyboardButton("Неиронично", callback_data="non_ironic"))
ironic_keyboard.row_width = 1

# Клавиатура для голосовашек
vote_keyboard = InlineKeyboardMarkup()
vote_keyboard.add(InlineKeyboardButton("За", callback_data="favor"))
vote_keyboard.add(InlineKeyboardButton("Против", callback_data="against"))
vote_keyboard.add(InlineKeyboardButton("Воздерживаюсь", callback_data="abstain"))
vote_keyboard.row_width = 1

# Тестовая клавиатура, кнопки не нажимаются
test_keyboard = InlineKeyboardMarkup()
test_keyboard.add(InlineKeyboardButton("Тестовая кнопка 1", callback_data="1"))
test_keyboard.add(InlineKeyboardButton("Тестовая кнопка 2", callback_data="2"))
test_keyboard.add(InlineKeyboardButton("Тестовая кнопка 3", callback_data="3"))
test_keyboard.row_width = 1

# Клавиатура для выбора, куда постить голосовашку
where_keyboard = InlineKeyboardMarkup()
where_keyboard.add(InlineKeyboardButton("Сюда", callback_data="here"))
where_keyboard.add(InlineKeyboardButton("В канал голосовашек", callback_data="there"))
where_keyboard.row_width = 1

# Клавиатура для выбора, куда постить мульти-голосовашку
m_where_keyboard = InlineKeyboardMarkup()
m_where_keyboard.add(InlineKeyboardButton("Сюда", callback_data="m_here"))
m_where_keyboard.add(InlineKeyboardButton("В канал голосовашек", callback_data="m_there"))
m_where_keyboard.row_width = 1

# Клавиатура для выбора, куда постить адапт-голосовашку
a_where_keyboard = InlineKeyboardMarkup()
a_where_keyboard.add(InlineKeyboardButton("Сюда", callback_data="a_here"))
a_where_keyboard.add(InlineKeyboardButton("В канал голосовашек", callback_data="a_there"))
a_where_keyboard.row_width = 1

# Клавиатура для признания предложения для мульти-голосовашки адекватным/неадекватным
adequate_keyboard = InlineKeyboardMarkup()
adequate_keyboard.add(InlineKeyboardButton("Адекватно", callback_data="adequate"))
adequate_keyboard.add(InlineKeyboardButton("Неадекватно", callback_data="inadequate"))
adequate_keyboard.row_width = 1

# Клавиатура для признания предложения для адапт-голосовашки адекватным/неадекватным
a_adequate_keyboard = InlineKeyboardMarkup()
a_adequate_keyboard.add(InlineKeyboardButton("Адекватно", callback_data="a_adequate"))
a_adequate_keyboard.add(InlineKeyboardButton("Неадекватно", callback_data="inadequate"))
a_adequate_keyboard.row_width = 1


# Список всех ролей и их подтипы
roles = ["Гость", "Гражданин", "Высший Гражданин", "Админ", "Член Комитета", "Заместитель", "Лидер"]
