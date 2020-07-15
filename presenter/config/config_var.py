# -*- coding: utf-8 -*-
"""Module with important constants"""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from presenter.config.log import Logger, LOG_TO
from presenter.config.texts import JANUARY, FEBRUARY, MARCH, APRIL, MAY, \
    JUNE, JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER

LOG = Logger(LOG_TO)

CREATOR_ID = 381279599

BOT_ID = 575704111

ENTITIES_TO_PARSE = {'bold', 'italic', 'underline', 'strikethrough', 'code', 'text_link'}

ORIGINAL_TO_ENGLISH = {'Русский': 'Russian', 'English': 'English'}
ENGLISH_TO_ORIGINAL = {'Russian': 'Русский', 'English': 'English'}
MONTHS = [
    JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE, JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER
]


def month_to_genitive(month: dict) -> dict:
    """Converts a month to genitive case"""
    if month['Russian'][-1] in ('й', 'ь'):
        nrm = month['Russian'][:-1].lower() + 'я'
        return {'Russian': nrm, 'English': month['English']}
    nrm = month['Russian'].lower() + 'а'
    return {'Russian': nrm, 'English': month['English']}


def month_to_prepositional(month: dict) -> dict:
    """Converts a month to prepositional case"""
    if month['Russian'][-1] in ('й', 'ь'):
        nrm = month['Russian'][:-1].lower() + 'е'
        return {'Russian': nrm, 'English': month['English']}
    nrm = month['Russian'].lower() + 'е'
    return {'Russian': nrm, 'English': month['English']}


MONTHS_GENITIVE = [month_to_genitive(i) for i in MONTHS]
MONTHS_PREPOSITIONAL = [month_to_prepositional(i) for i in MONTHS]


def admin_place(message, database):
    """Finds the admin place of the system"""
    LOG.log_print("admin_place invoked")
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    return database.get('systems', ('id', system))['admin_place']


def chat_list(database, system):
    """Список всех МФ2-чатов, кроме Админосостава и Комитета"""
    LOG.log_print("chat_list invoked")
    ch_list = database.get_many('chats', ('system', system))
    return ch_list


def full_chat_list(database, system):
    """Список всех МФ2-чатов"""
    LOG.log_print("full_chat_list invoked")
    return database.get_many('chats', ('system', system))


def channel_list(database):
    """Список всех МФ2-каналов"""
    return database.get_all('channels')


# список всех content_types для подсчёта сообщений
ALL_CONTENT_TYPES = [
    'text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location',
    'contact'
]

# Клавиатура для вопроса, иронично ли признание оскорбления/провокации
IRONIC_KEYBOARD = InlineKeyboardMarkup()
IRONIC_KEYBOARD.add(InlineKeyboardButton("Иронично", callback_data="ironic"))
IRONIC_KEYBOARD.add(InlineKeyboardButton("Неиронично", callback_data="non_ironic"))
IRONIC_KEYBOARD.row_width = 1

# Клавиатура для голосовашек
VOTE_KEYBOARD = InlineKeyboardMarkup()
VOTE_KEYBOARD.add(InlineKeyboardButton("За", callback_data="favor"))
VOTE_KEYBOARD.add(InlineKeyboardButton("Против", callback_data="against"))
VOTE_KEYBOARD.add(InlineKeyboardButton("Воздерживаюсь", callback_data="abstain"))
VOTE_KEYBOARD.row_width = 1

# Тестовая клавиатура, кнопки не нажимаются
TEST_KEYBOARD = InlineKeyboardMarkup()
TEST_KEYBOARD.add(InlineKeyboardButton("Тестовая кнопка 1", callback_data="1"))
TEST_KEYBOARD.add(InlineKeyboardButton("Тестовая кнопка 2", callback_data="2"))
TEST_KEYBOARD.add(InlineKeyboardButton("Тестовая кнопка 3", callback_data="3"))
TEST_KEYBOARD.row_width = 1

# Клавиатура для признания предложения для мульти-голосовашки адекватным/неадекватным
ADEQUATE_KEYBOARD = InlineKeyboardMarkup()
ADEQUATE_KEYBOARD.add(InlineKeyboardButton("Адекватно", callback_data="adequate"))
ADEQUATE_KEYBOARD.add(InlineKeyboardButton("Неадекватно", callback_data="inadequate"))
ADEQUATE_KEYBOARD.row_width = 1

# Клавиатура для признания предложения для адапт-голосовашки адекватным/неадекватным
ADAPT_ADEQUATE_KEYBOARD = InlineKeyboardMarkup()
ADAPT_ADEQUATE_KEYBOARD.add(InlineKeyboardButton("Адекватно", callback_data="a_adequate"))
ADAPT_ADEQUATE_KEYBOARD.add(InlineKeyboardButton("Неадекватно", callback_data="inadequate"))
ADAPT_ADEQUATE_KEYBOARD.row_width = 1

ADD_CHAT_KEYBOARD = InlineKeyboardMarkup()
ADD_CHAT_KEYBOARD.add(InlineKeyboardButton("Новый чат", callback_data="new_chat"))
ADD_CHAT_KEYBOARD.add(InlineKeyboardButton("Часть другого чата",
                                           callback_data="part_of_other_chat"))
ADD_CHAT_KEYBOARD.row_width = 1

FEATURES = ('standart_commands', 'erotic_commands', 'boss_commands', 'financial_commands',
            'mutual_invites', 'messages_count', 'violators_ban', 'admins_promote', 'moves_delete',
            'newbies_captched')
FEATURES_TEXTS = dict()
FEATURES_TEXTS['Russian'] = [
    'Разлекательные команды', 'Эротические команды', 'Админские команды (/ban, /warn...)',
    'Денежные команды (/pay, /give, /fund)',
    'Ссылка учитывается', 'Сообщения считаются',
    'Нарушители банятся при входе', 'Админы получают админку',
    'Сообщения о входе и выходе удаляются '
    '(если вкл, а капча выкл, бот не будет здороваться)', 'Новички проходят капчу'
]
FEATURES_TEXTS['English'] = [
    'Standart commands', 'Admin commands', 'Financial commands', 'Invites links',
    'Messages are count for citizenship', 'MF2 violators are automatically banned',
    'MF2 admins are automatically promoted'
]

FEATURES_ONERS = tuple(map(lambda x: x + '_on', FEATURES))
FEATURES_OFFERS = tuple(map(lambda x: x + '_off', FEATURES))
FEATURES_DEFAULTERS = tuple(map(lambda x: x + '_default', FEATURES))
SYSTEM_FEATURES_ONERS = tuple(map(lambda x: 's_' + x + '_on', FEATURES))
SYSTEM_FEATURES_OFFERS = tuple(map(lambda x: 's_' + x + '_off', FEATURES))

NEW_SYSTEM_JSON_ENTRY = {
    "name": "",
    "money": False,
    "money_emoji": "💰",
    "money_name": "валюты",
    "ranks": ["Забаненный", "Участник", "Админ", "Старший Админ", "Лидер"],
    "ranks_commands": [None, "/guest", "/admin", "/senior_admin", "/leader"],
    "appointments": [],
    "appointment_adders": [],
    "appointment_removers": [],
    "commands": {
        "standart": ["Участник", "Лидер"],
        "advanced": ["Участник", "Лидер"],
        "boss": ["Админ", "Лидер"],
        "uber": ["Старший Админ", "Лидер"],
        "chat_changer": ["Админ", "Лидер"]
    },
    "greetings": {
        "standart": "Добро пожаловать, {name}",
        "captcha": "Добро пожаловать, {name}. Докажите, что не бот, "
                   "нажмите на КРЕВЕТКУ за 5 минут",
        "admin": "О, добро пожаловать, держи админку",
        "full_admin": "О, добро пожаловать, держи полную админку"
    }
}
