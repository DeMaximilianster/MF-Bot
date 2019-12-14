# -*- coding: utf-8 -*-
from presenter.config.log import Loger, log_to
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from presenter.config.texts import january, february, march, april, may, june, july, august, september, october,\
    november, december

log = Loger(log_to)

bot_id = 575704111

original_to_english = {'Русский': 'Russian', 'English': 'English'}
english_to_original = {'Russian': 'Русский', 'English': 'English'}
months = ['No Month', january, february, march, april, may, june, july, august, september, october, november, december]


def admin_place(database):
    log.log_print(f"{__name__} invoked")
    return database.get('chats', ('purpose', "Админосостав"))[0]


def chat_list(database):  # TODO Сделать приличную чатоискалку
    """Список всех МФ2-чатов, кроме Админосостава и Комитета"""
    log.log_print(f"{__name__} invoked")
    ch_list = database.get_many('chats', ('boss_commands', 2), ('violators_ban', 2), ('admins_promoted', 2))
    return ch_list


def full_chat_list(database):
    """Список всех МФ2-чатов"""
    log.log_print(f"{__name__} invoked")
    return database.get_all('chats')


def channel_list(database):
    """Список всех МФ2-каналов"""
    return database.get_all('channels')


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
where_keyboard.add(InlineKeyboardButton("На канал голосовашек", callback_data="there"))
where_keyboard.add(InlineKeyboardButton("На канал недостримов", callback_data="nedostream"))
where_keyboard.row_width = 1

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
roles = [None, 'Violator', 'Guest', 'Citizen', 'Senior Citizen', 'The Committee Member', 'Deputy', 'Leader']
