"""Standart commands, available for everyone"""
# -*- coding: utf-8 -*-
from random import choice
from view.output import reply, send_photo, send_sticker, send, send_video, send_document
from presenter.config.config_func import member_update, int_check, \
    is_suitable, feature_is_available, get_system_configs, get_systems_json, get_person, \
    get_list_from_storage, number_to_case, case_analyzer, person_link, \
    html_cleaner, link_text_wrapper, function_returned_true, value_marker, get_storage_json
from presenter.config.database_lib import Database
from presenter.config.config_var import admin_place, ORIGINAL_TO_ENGLISH, ENGLISH_TO_ORIGINAL, \
    MONTHS_GENITIVE, MONTHS_PREPOSITIONAL, FEATURES, FEATURES_TEXTS
from presenter.config.log import Loger
from presenter.config.texts import MINETS

LOG = Loger()


def language_setter(message):
    """Gets the language of the chat"""
    LOG.log_print("language_getter invoked")
    database = Database()
    original_languages = ['Русский', 'English']
    english_languages = ['Russian', 'English']
    language = message.text[6:].title()
    if language in original_languages + english_languages:
        if language in original_languages:
            language = (language, ORIGINAL_TO_ENGLISH[language])
        else:  # language in english_languages
            language = (ENGLISH_TO_ORIGINAL[language], language)
        if database.get('languages', ('id', message.chat.id)):
            database.change(language[1], 'language', 'languages', ('id', message.chat.id))
        else:
            database.append((message.chat.id, language[1]), 'languages')
        if language[0] == language[1]:
            reply(message, f"✅ {language[0]} ✅")
        else:
            reply(message, f"✅ {language[0]} | {language[1]} ✅")
    else:
        answer = ''
        answer += "Если вы говорите на русском, напишите '/lang Русский'\n\n"
        answer += "If you speak English, type '/lang English'\n\n"
        reply(message, answer)


def helper(message):
    """Предоставляет человеку список команд"""
    LOG.log_print(str(message.from_user.id) + ": helper invoked")
    database = Database()
    # TODO Возможность посмотреть номер своей системы
    # TODO Адаптативность званий
    answer = '<b>Команды:</b>\n\n'
    if message.chat.id < 0:  # Command is used in chat
        system = database.get('chats', ('id', message.chat.id))['system']

        answer += '<b>Общие команды:</b>\n' \
                  '/me - Присылает вашу запись в базе данных\n' \
                  '/anon - Прислать анонимное послание в админский чат (если таковой имеется)\n' \
                  '/members - Прислать в личку перечень участников (нынешних и бывших) и их ID\n' \
                  '/messages_top - Прислать в личку топ участников по сообщениям\n' \
                  '/warns - Посмотреть, у кого сколько предупреждений\n\n'
        # Helps
        answer += '<b>Помощь и менюшки:</b>\n'
        answer += '/help - Прислать это сообщение\n'
        answer += '/money_help - Финансовый режим\n'
        answer += '/chat - Показать настройки в чате\n'
        answer += '/system - Показать настройки по умолчанию\n\n'\
                  '<b>Хранилище:</b>\n'\
                  '/storages - Посмотреть список хранилищ\n'\
                  '/get [хранилище] - Получать случайный контент из хранилища\n'\
                  '/size [хранилище] - Получить инфо о количестве контента и модеров хранилища\n\n'
        if feature_is_available(message.chat.id, system, 'standart_commands'):
            answer += '<b>Развлекательные команды:</b>\n'
            answer += '/minet - Делает приятно\n'
            answer += '/meme - Присылает мем\n'
        if is_suitable(message, message.from_user, 'boss', loud=False):
            answer += '<b>Базовые админские команды:</b>\n'
            answer += '/update - Пересчитывает сообщения, ' \
                      'никнеймы и юзернеймы всех участников чата\n'
            answer += '/messages [число сообщений] - ' \
                      'Изменить количество сообщений от участника в этом чате\n'
            answer += '/warn [число варнов]- Дать варн(ы) (3 варна = бан)\n'
            answer += '/unwarn [число варнов]- Снять варн(ы)\n'
            answer += '/mute [количество часов] - Запретить писать в чат\n'
            answer += '/ban - Дать бан\n'
            answer += '/kick - Кикнуть (то есть чел сразу сможет вернуться)\n'
            answer += '/guest - Снять ограничения, забрать админку\n\n'
        if is_suitable(message, message.from_user, 'uber', loud=False):
            answer += '<b>Продвинутые админские команды:</b>\n'
            answer += '/admin - Снять ограничения, дать админку\n'
            answer += '/senior_admin - Снять бан, дать продвинутую админку\n\n'
        if is_suitable(message, message.from_user, 'chat_changer', loud=False):
            answer += '<b>Настройщики чатов:</b>\n'
            answer += '/add_chat [номер системы чатов] - Добавить чат в систему чатов\n'
            answer += '/admin_place - Отметить чат как админский\n'
            answer += '/standart_greetings [текст] — Изменить приветствие для простого человека\n' \
                      '/captcha_greetings [текст] — Изменить приветствие при капче\n' \
                      '/admin_greetings [текст] — Изменить приветствие для админа\n' \
                      '/full_greetings [текст] — Изменить приветствие для полного админа\n' \
                      "<i>Вставьте в текст '{name}' без кавычек там, " \
                      "где нужно обратиться к участнику по нику</i>\n\n"

        answer += "<b>Примечание:</b> " \
                  "командами типа /me можно отвечать на сообщения других людей, " \
                  "тогда команда выполнится на выбранном человеке. " \
                  "Ещё вы можете после команды написать ID человека (можно достать " \
                  "в /members), чтобы не отвлекать его от дел :3"
    else:  # Command is used in PM
        answer += '/help - Прислать это сообщение\n'
        answer += '/minet - Делает приятно\n'
        answer += '/drakken - Присылает арт с Доктором Драккеном\n'
        answer += '/meme - Присылает мем\n'
        answer += '/art - Присылает картину\n'
        answer += '/storages - Посмотреть список хранилищ'
        answer += '/get [хранилище] - Получать случайный контент из хранилища'
        answer += '/size [хранилище] - Получить инфо о количестве контента и модеров хранилища'
        answer += 'В чате мой функционал значительно шире'
    reply(message, answer, parse_mode='HTML')


def money_helper(message):
    """Help with financial commands"""
    answer = "<b>Финансовые команды:</b>\n\n"
    answer += "/money_off - Выключить финансовый режим\n"
    answer += '/money_on [Кол-во денег] - Включить финансовый режим с заданным бюджетом ' \
              'или обновить бюджет\n'
    answer += '[Казна] = [Кол-во денег] - [Деньги участников]\n'
    answer += 'Если кол-во денег не указано, будет установлена бесконечная казна\n\n'
    answer += '/m_emoji [Смайлик или короткий текст] - Поставить сокращение валюты\n'
    answer += '/m_name [Название] - Поставить название валюты ' \
              '(им. падеж, ед. число, например доллар, рубль, гривна)\n'

    answer += '/top - Получить топ людей по валюте\n\n'

    answer += '/pay [Кол-во] - Заплатить челу. Если деньги не вечны, то берутся из казны.' \
              'Забрать деньги тоже можно\n' \
              '/give [Кол-во] - Дать челу деньги из вашего личного счёта\n' \
              '/fund [Кол-во] - Заплатить в фонд чата\n\n'

    answer += '/money_reset - Обнулить деньги всех участников и вернуть их в казну'

    reply(message, answer, parse_mode='HTML')


def send_list_of_storages(message):
    """ Sends list of all storages """
    LOG.log_print("send_list_of_storages invoked")
    storages_dict = get_storage_json()
    vulgar_storages = []
    non_vulgar_storages = []
    for storage in storages_dict:
        if storages_dict[storage]['is_vulgar']:
            vulgar_storages.append(storage)
        else:
            non_vulgar_storages.append(storage)
    str_vulgar_storages = '<code>' + '</code>, <code>'.join(vulgar_storages) + '</code>'
    str_non_vulgar_storages = '<code>' + '</code>, <code>'.join(non_vulgar_storages) + '</code>'
    text = "Обычные хранилища: {}\n\nЭротичные хранилища: {}".format(
        str_non_vulgar_storages, str_vulgar_storages)
    reply(message, text, parse_mode='HTML')


def minet(message, language):
    """Приносит удовольствие"""
    LOG.log_print(str(message.from_user.id) + ": minet invoked")
    if language:
        choices = []
        for i in MINETS[language].keys():
            choices.append(i)
        way = choice(choices)
        rep = choice(MINETS[language][way])
        if way == 'text':
            reply(message, rep)
        else:
            send_sticker(message.chat.id, rep, reply_to_message_id=message.message_id)


def send_stuff_from_storage(message, storage_name):
    """Send a piece of media from a storage"""
    LOG.log_print("send_stuff_from_storage invoked")
    contents = get_list_from_storage(storage_name)['contents']
    if len(contents) > 0:
        result = choice(contents)
        args_to_send = [message.chat.id, result[0]]
        kwargs_to_send = {'reply_to_message_id': message.message_id,
                          'caption': result[2], 'parse_mode': 'HTML'}
        if result[1] == 'photo':
            send_photo(*args_to_send, **kwargs_to_send)
        elif result[1] == 'video':
            send_video(*args_to_send, **kwargs_to_send)
        elif result[1] == 'gif':
            send_document(*args_to_send, **kwargs_to_send)
        else:
            reply(message, "Произошла ошибка!")
    else:
        reply(message, "На данный момент хранилище пусто :-(")


def check_storage_size(message, storage_name):
    """ Checks how many moderators and how much media there is in a storage """
    LOG.log_print('check_storage_size invoked')
    storage = get_list_from_storage(storage_name)
    moderators_number = len(storage['moders'])
    media_number = len(storage['contents'])
    moderator = case_analyzer('модератор', 'Russian', *number_to_case(moderators_number, 'Russian'))
    reply(message, "На данный момент в хранилище {} {} медиа и {} {}".format(
        storage_name, media_number, moderators_number, moderator))


def send_meme(message):
    """Присылает мем"""
    LOG.log_print(str(message.from_user.id) + ": send_meme invoked")
    meme = choice(('AgADAgADx60xG2S_oUmVz41Dk8a4AkRNUw8ABAEAAwIAA20AAzj4BQABFgQ',
                   'AgADAgADdKsxG7PUsEmfWmu7wYQaSlHNuQ8ABAEAAwIAA20AA2gAAxYE',
                   'AgADAgAD-aoxG0EnIUqnHKx1l-EFFajiug8ABAEAAwIAA20AA3VUAAIWBA',
                   'AgADAgADY6sxG2RPyUmfTbFEJLvRV9Lhtw8ABAEAAwIAA20AA-lxAQABFgQ',
                   'AgADAgAD36sxG3h0uUlOXJnN-wooZiGxhQ8ABAEAAwIAA3gAA7nOAgABFgQ',
                   'AgADAgADJKsxG-KVuElBSmME_b_Cn8KghQ8ABAEAAwIAA20AA2DOAgABFgQ'))
    send_photo(message.chat.id, meme, reply_to_message_id=message.message_id)


def send_me(message, person):
    """Присылает человеку его запись в БД"""
    LOG.log_print(str(message.from_user.id) + ": send_me invoked")
    database = Database()
    system = database.get('chats', ('id', message.chat.id))['system']
    chat_config = get_system_configs(system)
    money_name = chat_config['money_name']
    member_update(system, person)  # Update person's messages, nickname and username
    person_entry = get_person(person, system, database, system_configs=chat_config)
    appointments = [x['appointment'] for x in
                    database.get_many('appointments', ('id', person.id), ('system', system))]
    messages_here = 0
    if database.get('messages', ('person_id', person.id), ('chat_id', message.chat.id)):
        messages_here = database.get('messages', ('person_id', person.id),
                                     ('chat_id', message.chat.id))['messages']
    msg = 'ID: {}\n'.format(person_entry['id'])
    msg += 'Юзернейм: {}\n'.format(person_entry['username'])
    msg += 'Никнейм: {}\n'.format(person_entry['nickname'])
    msg += 'Ранг: {}\n'.format(person_entry['rank'])
    msg += 'Кол-во сообщений в этом чате: {}\n'.format(messages_here)
    if person_entry['messages']:
        msg += 'Кол-во сообщений во всей системе: {}\n'.format(person_entry['messages'])
    msg += 'Кол-во предупреждений: {}\n'.format(person_entry['warns'])
    if chat_config['money']:
        msg += 'Кол-во {}: {}\n'.format(case_analyzer(money_name, 'Russian', 'plural', 'genitivus'),
                                        person_entry['money'])
    if appointments:
        msg += 'Должности: ' + ', '.join(appointments)
    reply(message, msg)


def send_some_top(message, language, format_string, start='', sort_key=lambda x: True):
    """Send a full version of a top for admins"""
    # TODO Кто вышел из чата, а кто находится в чате
    LOG.log_print("send_some_top invoked")
    database = Database()
    # Declaring variables
    sent = False
    system = database.get('chats', ('id', message.chat.id))['system']
    formating_dict = {'m_emo': get_system_configs(system)['money_emoji'],
                      'bot_money': database.get('systems', ('id', system))['money']}
    text = start.format(**formating_dict)
    members = database.get_many('members', ('system', system))
    members = list(filter(lambda x: function_returned_true(sort_key, x), members))
    members.sort(key=sort_key, reverse=True)
    if len(members) > 50:
        target_chat = message.from_user.id
    else:
        target_chat = message.chat.id
    # Main loop
    for index in range(1, len(members) + 1):
        member = members[index - 1]
        p_link = link_text_wrapper(html_cleaner(member["nickname"]), f't.me/{member["username"]}')
        formating_dict.update(member)
        formating_dict.update({'index': index, 'p_link': p_link, 'day': member['day_birthday']})
        if '{month}' in format_string:
            formating_dict['month'] = MONTHS_GENITIVE[member['month_birthday'] - 1][language]
        text += format_string.format(**formating_dict)
        if index % 50 == 0:
            sent = send(target_chat, text, parse_mode='HTML')
            text = ''
    sent = send(target_chat, text, parse_mode='HTML') or sent
    if len(members) > 50:
        if sent:
            reply(message, "Выслал инфу в личку")
        else:
            reply(message, "Сначала запусти меня в личных сообщениях")
    elif not sent:
        reply(message, "Ничего нет!")


def send_short_top(message, language, format_string, start='', sort_key=lambda x: True):
    """Send a short version of a top for non-admins"""
    LOG.log_print("send_short_top invoked")
    database = Database()
    # Declaring variables
    system = database.get('chats', ('id', message.chat.id))['system']
    formating_dict = {'m_emo': get_system_configs(system)['money_emoji'],
                      'bot_money': database.get('systems', ('id', system))['money']}
    text = start.format(**formating_dict)
    members = database.get_many('members', ('system', system))
    members = list(filter(lambda x: function_returned_true(sort_key, x), members))
    members.sort(key=sort_key, reverse=True)
    person_index = 0
    for person_index in range(1, len(members) + 1):
        if members[person_index - 1]['id'] == message.from_user.id:
            break
    # Main loop
    for index in range(1, len(members) + 1):
        member = members[index - 1]
        p_link = link_text_wrapper(html_cleaner(member["nickname"]), f't.me/{member["username"]}')
        formating_dict.update(member)
        formating_dict.update({'index': index, 'p_link': p_link, 'day': member['day_birthday']})
        if '{month}' in format_string:
            formating_dict['month'] = MONTHS_GENITIVE[member['month_birthday'] - 1][language]
        if index <= 5 or abs(index - person_index) <= 2:
            text += format_string.format(**formating_dict)
        elif '.\n.\n.\n' not in text and person_index >= 9:
            text += '.\n.\n.\n'
    if text:
        send(message.chat.id, text, parse_mode='HTML')
    else:
        reply(message, "Ничего нет!")


def money_give(message, person, parameters_dictionary: dict):
    """Функция обмена деньгами между людьми"""
    LOG.log_print(f"money_give invoked to person {person.id}")
    database = Database()
    getter = person
    giver = message.from_user
    money = parameters_dictionary['value']
    system = database.get('chats', ('id', message.chat.id))['system']
    # TODO Replace these strings in each 3 money function with get_person()
    value_getter = database.get('members', ('id', getter.id), ('system', system))['money']
    value_giver = database.get('members', ('id', giver.id), ('system', system))['money']
    #
    money_name = get_system_configs(system)['money_name']
    number_and_case = number_to_case(money, 'Russian')
    money_name_plural_genitivus = case_analyzer(money_name, 'Russian', 'plural', 'genitivus')
    money_name = case_analyzer(money_name, 'Russian', *number_and_case)
    if money < 0:
        reply(message, "Я вам запрещаю воровать")
    elif money == 0:
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
    else:
        if money > value_giver:
            reply(message, "Не хватает {}".format(money_name_plural_genitivus))
        else:
            value_getter += money
            value_giver -= money
            giv_m = send(giver.id, "#Финансы\n\nВы успешно перевели {} {} на счёт {}. "
                                   "Теперь у вас их {}".format(money, money_name,
                                                               person_link(getter), value_giver),
                         parse_mode='HTML')
            get_m = send(getter.id, "#Финансы\n\nНа ваш счёт переведено {} {} со счёта {}. "
                                    "Теперь у вас их {}".format(money, money_name,
                                                                person_link(giver), value_getter),
                         parse_mode='HTML')
            if get_m:
                get_m = "🔔 уведомлён(а)"
            else:
                get_m = "🔕 не уведомлён(а)"
            if giv_m:
                giv_m = "🔔 уведомлён(а)"
            else:
                giv_m = "🔕 не уведомлён(а)"
            reply(message, "{} передал(а) {} {} {}!".
                  format(person_link(giver), person_link(getter), money, money_name),
                  parse_mode='HTML')
            send(admin_place(message, database),
                 f"#Финансы #f{getter.id} #f{giver.id}\n\n"
                 f"{person_link(getter)} [{value_getter - money} --> {value_getter}] {get_m}\n"
                 f"{person_link(giver)} [{value_giver + money} --> {value_giver}] {giv_m}\n",
                 parse_mode='HTML')
    database.change(value_getter, 'money', 'members', ('id', getter.id), ('system', system))
    database.change(value_giver, 'money', 'members', ('id', giver.id), ('system', system))


def money_fund(message, parameters_dictionary):
    """Transfer money to the chat fund"""
    LOG.log_print("money_fund invoked")
    database = Database()

    giver = message.from_user
    money = parameters_dictionary['value']
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    value_giver = database.get('members', ('id', giver.id), ('system', system))['money']
    value_system = database.get('systems', ('id', system))['money']
    money_name = get_system_configs(system)['money_name']
    number_and_case = number_to_case(money, 'Russian')
    money_name_plural_genitivus = case_analyzer(money_name, 'Russian', 'plural', 'genitivus')
    money_name = case_analyzer(money_name, 'Russian', *number_and_case)
    if money < 0:
        reply(message, "Я вам запрещаю воровать")
    elif money == 0:
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
    else:
        if money > value_giver:
            reply(message, "Не хватает {}".format(money_name_plural_genitivus))
        else:
            if value_system != 'inf':
                value_system = int(value_system)
                value_system += money
            value_giver -= money
            text = f"#Финансы\n\nВы успешно перевели {money} {money_name} в фонд чата. " \
                   f"Теперь у вас их {value_giver}"
            giv_m = value_marker(send(giver.id, text), "🔔 уведомлён(а)", "🔕 не уведомлён(а)")

            reply(message, "{} заплатил(а) в банк {} {}!".format(person_link(giver),
                                                                 money, money_name),
                  parse_mode='HTML')
            answer = f"#Финансы #f{giver.id}\n\n"
            if value_system != 'inf':
                answer += f"#Бюджет [{value_system - money} --> {value_system}]\n"
            answer += f"{person_link(giver)} [{value_giver + money} --> {value_giver}] {giv_m}\n"
            send(admin_place(message, database), answer, parse_mode='HTML')
            database.change(value_giver, 'money', 'members', ('id', giver.id), ('system', system))
            database.change(value_system, 'money', 'systems', ('id', system))


# TODO More comfortable way to insert birthday
def month_set(message, month):
    """Set the month of person's birthday"""
    LOG.log_print(f"month_set invoked")
    database = Database()
    reply(message, "Ставлю человеку с ID {} месяц рождения {}".format(message.from_user.id, month))
    database.change(month, 'month_birthday', 'members', ('id', message.from_user.id))


def day_set(message, day, language):
    """Set the day of person's birthday"""
    LOG.log_print(f"day_set invoked")
    days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    database = Database()
    month = database.get('members', ('id', message.from_user.id))['month_birthday'] - 1
    if not month:
        reply(message, "Сначала поставь месяц рождения")
    elif day > days[month]:
        month = MONTHS_PREPOSITIONAL[month][language]
        reply(message, "В {} нет столько дней".format(month.lower()))
    else:
        reply(message, "Ставлю человеку с ID {} день рождения {}".format(message.from_user.id, day))
        database.change(day, 'day_birthday', 'members', ('id', message.from_user.id))


def admins(message):
    """@-mention all admins"""
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    chat_config = get_system_configs(system)
    boss = chat_config['commands']['boss']
    ranks = chat_config['ranks']
    admins_username = []
    if isinstance(boss, list):
        all_ranks = ranks[ranks.index(boss[0]):ranks.index(boss[1]) + 1]
        for rank in all_ranks:
            admins_username += ['@' + x['username'] for x in
                                database.get_many('members', ('rank', rank), ('system', system))]
    elif isinstance(boss, str):
        admins_id = [admin['id'] for admin in
                     database.get_many('appointments', ('appointment', boss))]
        admins_username = [
            '@' + database.get('members', ('id', admin), ('system', system))['username'] for admin
            in
            admins_id]
    reply(message, 'Вызываю сюда админов: ' + ', '.join(admins_username))


def chats(message):
    """Get list of chats"""
    database = Database()
    chats_list = database.get_many('chats', ('type', 'public'))

    # Получаем имена и ссылки нужных нам чатиков
    chats_names = [chat['name'] for chat in chats_list]
    chats_links = ['@' + chat['link'] for chat in chats_list]

    # Генерируем текст для отображение имен и ссылок вместе
    text = '\n'.join([f'{key}: {value}' for key, value in zip(chats_names, chats_links)])
    reply(message, text)


def chat_check(message):
    """Show which options are chosen in chat"""
    database = Database()
    # TODO Сделать функцию для обновы чата
    database.change(message.chat.title, 'name', 'chats', ('id', message.chat.id))
    if message.chat.username:
        database.change('public', 'type', 'chats', ('id', message.chat.id))
        database.change(message.chat.username, 'link', 'chats', ('id', message.chat.id))
    else:
        database.change('private', 'type', 'chats', ('id', message.chat.id))
        database.change('None', 'link', 'chats', ('id', message.chat.id))
    # Здесь конец
    chat = database.get('chats', ('id', message.chat.id))
    system = database.get('systems', ('id', chat['system']))
    text = 'Настройки этого чата:\n\n'
    for feature in FEATURES:
        mark = ''
        microtext = ''
        system_property = system[feature]
        chat_property = chat[feature]
        if system_property:  # Feature is suggested
            if chat_property == 2:  # Feature is set default
                mark += '⚙'
                microtext += ' (по умолчанию)'
                chat_property = system_property - 1
            if chat_property:
                mark = '✅' + mark
                microtext = 'Работает' + microtext
            else:
                mark = '❌' + mark
                microtext = 'Не работает' + microtext
            text += f"{FEATURES_TEXTS['Russian'][FEATURES.index(feature)]}: \n{mark} {microtext}\n"
            if '⚙' in mark or '❌' in mark:
                text += f"/{feature}_on Включить на постоянку\n"
            if '⚙' in mark or '✅' in mark:
                text += f"/{feature}_off Выключить на постоянку\n"
            if '⚙' not in mark:
                text += f"/{feature}_default Поставить значение по умолчанию\n"
            text += '\n'
    reply(message, text)


def system_check(message):
    """Show which options are chosen in system"""
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = database.get('systems', ('id', chat['system']))
    print(system)
    text = 'Настройки по умолчанию:\n\n'
    for feature in FEATURES:
        system_property = system[feature]
        if system_property == 2:
            text += f"{FEATURES_TEXTS['Russian'][FEATURES.index(feature)]}: \n✅ Включено\n"
            text += f"/s_{feature}_off Выключить\n\n"
        elif system_property == 1:
            text += f"{FEATURES_TEXTS['Russian'][FEATURES.index(feature)]}: \n❌ Выключено\n"
            text += f"/s_{feature}_on Включить\n\n"
    reply(message, text)


def anon_message(message):
    """Send an anonymous message to an admin place"""
    LOG.log_print('anon_message invoked')
    database = Database(to_log=False)
    systems = [x['system'] for x in database.get_many('members', ('id', message.from_user.id))]
    system = None
    system_specification_length = 0
    if len(systems) == 1:
        system = systems[0]
    elif int_check(message.text.split()[1], positive=True):
        system = message.text.split()[1]
        system_specification_length += len(system) + 1
    else:
        data = get_systems_json()
        text = "Вижу вы сидите в нескольких чатах. " \
               "Чтобы уточнить, в какой админосостав отправлять сообщение, " \
               "оформите вашу команду так:\n\n/anon <номер системы> <ваше послание>.\n\n " \
               "Вот список систем:\n"
        names = [f"{sys} — {data[sys]['name']}" for sys in systems]
        reply(message, text + '\n'.join(names))
    if system:
        system_entry = database.get('systems', ('id', system))
        if system_entry:
            if system_entry['admin_place']:
                anon_message_text = ' '.join(message.text.split()[1:])
                sent = send(system_entry['admin_place'],
                            "#anon\n\n" + anon_message_text[system_specification_length:])
                if sent:
                    reply(message, "Сообщение успешно отправлено. Спасибо за ваше мнение!")
                else:
                    reply(message, "Произошла ошибка!")
            else:
                reply(message, "У этой системы админосостав не отмечен")
        else:
            reply(message, "Этой системы не существует!")
