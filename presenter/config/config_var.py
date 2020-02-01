# -*- coding: utf-8 -*-
from presenter.config.log import Loger, log_to
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from presenter.config.texts import january, february, march, april, may, june, july, august, september, october, \
    november, december

log = Loger(log_to)

bot_id = 575704111
porn_adders = (918715899, 381279599, 711157379)
stuff_adders = (918715899, 381279599, 432348248)

original_to_english = {'Русский': 'Russian', 'English': 'English'}
english_to_original = {'Russian': 'Русский', 'English': 'English'}
months = ['No Month', january, february, march, april, may, june, july, august, september, october, november, december]


def admin_place(message, database):
    log.log_print(f"admin_place invoked")
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    return database.get('systems', ('id', system))['admin_place']


def chat_list(database, system):  # TODO Сделать приличную чатоискалку
    """Список всех МФ2-чатов, кроме Админосостава и Комитета"""
    log.log_print(f"chat_list invoked")
    ch_list = database.get_many('chats', ('system', system))
    return ch_list


def full_chat_list(database, system):
    """Список всех МФ2-чатов"""
    log.log_print(f"full_chat_list invoked")
    return database.get_many('chats', ('system', system))


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

features = ('standart_commands', 'erotic_commands', 'boss_commands', 'financial_commands',
            'mutual_invites', 'messages_count', 'violators_ban', 'admins_promote', 'moves_delete', 'newbies_captched')
features_texts = dict()
features_texts['Russian'] = ['Разлекательные команды', 'Эротические команды',
                             'Админские команды', 'Денежные команды', 'Ссылка учитывается',
                             'Сообщения считаются', 'Нарушители банятся', 'Админы получают админку',
                             'Сообщения о входе и выходе удаляются (если вкл, а капча выкл, бот не будет здороваться)',
                             'Новички проходят капчу']
features_texts['English'] = ['Standart commands', 'Admin commands', 'Financial commands',
                             'Invites links', 'Messages are count for citizenship',
                             'MF2 violators are automatically banned', 'MF2 admins are automatically promoted']

features_oners = tuple(map(lambda x: x+'_on', features))
features_offers = tuple(map(lambda x: x+'_off', features))
features_defaulters = tuple(map(lambda x: x+'_default', features))
system_features_oners = tuple(map(lambda x: 's_'+x+'_on', features))
system_features_offers = tuple(map(lambda x: 's_'+x+'_off', features))

new_system_json_entry = {"name": "", "money": False, "money_emoji": "💰", "money_name": "валюты",
                         "ranks": ["Забаненный", "Участник", "Админ", "Старший Админ", "Лидер"],
                         "ranks_commands": [None, "/guest", "/admin", "/senior_admin", "/leader"],
                         "appointments": [],
                         "appointment_adders": [],
                         "appointment_removers": [],
                         "commands": {"standart": ["Участник", "Лидер"],
                                      "advanced": ["Участник", "Лидер"],
                                      "boss": ["Админ", "Лидер"],
                                      "uber": ["Старший Админ", "Лидер"],
                                      "chat_changer": ["Старший Админ", "Лидер"]},
                         "greetings": {"standart": "Добро пожаловать, {name}",
                                       "captcha":
                                       "Добро пожаловать, {name}. Докажите, что не бот, нажмите на КРЕВЕТКУ за 5 минут",
                                       "admin": "О, добро пожаловать, держи админку",
                                       "full_admin": "О, добро пожаловать, держи полную админку"}}
