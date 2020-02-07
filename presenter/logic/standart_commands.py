# -*- coding: utf-8 -*-
from view.output import reply, send_photo, send_sticker, send, send_video, send_document
from presenter.config.config_func import member_update, int_check, \
    is_suitable, feature_is_available, get_system_configs, get_systems_json, get_person, get_list_from_storage,\
    html_cleaner, link_text_wrapper, function_worked_correctly
from presenter.config.database_lib import Database
from presenter.config.config_var import admin_place, original_to_english, english_to_original, \
    months_genitive, months_prepositional, features, features_texts
from random import choice
from presenter.config.log import Loger
from presenter.config.texts import minets

log = Loger()


def language_getter(message):
    """Gets the language of the chat"""
    log.log_print("language_getter invoked")
    original_languages = ['Русский', 'English']
    english_languages = ['Russian', 'English']
    language = message.text[6:].title()
    if language in original_languages:
        language = (language, original_to_english[language])
    elif language in english_languages:
        language = (english_to_original[language], language)
    else:
        answer = ''
        answer += "Если вы говорите на русском, напишите '/lang Русский'\n\n"
        answer += "If you speak English, type '/lang English'\n\n"
        reply(message, answer)
        return None
    database = Database()
    if database.get('languages', ('id', message.chat.id)):
        database.change(language[1], 'language', 'languages', ('id', message.chat.id))
    else:
        database.append((message.chat.id, language[1]), 'languages')
    if language[0] == language[1]:
        reply(message, f"✅ {language[0]} ✅")
    else:
        reply(message, f"✅ {language[0]} | {language[1]} ✅")


def helper(message):
    """Предоставляет человеку список команд"""
    log.log_print(str(message.from_user.id) + ": helper invoked")
    database = Database()
    answer = '<b>Команды:</b>\n\n'
    if message.chat.id < 0:  # Command is used in chat
        system = database.get('chats', ('id', message.chat.id))['system']

        answer += '<b>Общие команды:</b>\n'
        answer += '/me - Присылает вашу запись в базе данных\n'
        answer += '/anon - Прислать анонимное послание в админский чат (если таковой имеется)\n'
        answer += '/members - Прислать в личку перечень участников (нынешних и бывших) и их ID\n'
        answer += '/messages_top - Прмслать в личку топ участников по сообщениям\n\n'
        # Helps
        answer += '<b>Помощь и менюшки:</b>\n'
        answer += '/help - Прислать это сообщение\n'
        answer += '/money_help - Финансовый режим\n'
        answer += '/chat - Показать настройки в чате\n'
        answer += '/system - Показать настройки по умолчанию\n\n'
        if feature_is_available(message.chat.id, system, 'standart_commands'):
            answer += '<b>Развлекательные команды:</b>\n'
            answer += '/minet - Делает приятно\n'
            answer += '/drakken - Присылает арт с Доктором Драккеном\n'
            answer += '/meme - Присылает мем\n'
            answer += '/art - Присылает картину\n\n'
        if feature_is_available(message.chat.id, system, 'erotic_commands'):
            answer += '<b>Эротические команды:</b>\n'
            answer += '/breasts - Присылает грудь\n'
            answer += '/ass - Присылает задницу\n\n'
        if is_suitable(message, message.from_user, 'boss', loud=False):
            answer += '<b>Базовые админские команды:</b>\n'
            answer += '/update - Пересчитывает сообщения, никнеймы и юзернеймы всех участников чата\n'
            answer += '/messages [число сообщений] - Изменить количество сообщений от участника в этом чате\n'
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
            answer += '/admin_place - Отметить чат как админский\n\n'
        answer += "<b>Примечание:</b> командами типа /me можно отвечать на сообщения других людей, тогда команда "
        answer += "выполнится на выбранном человеке. Ещё вы можете после команды написать ID человека (можно достать "
        answer += "в /members), чтобы не отвлекать его от дел :3"
    else:  # Command is used in PM
        answer += '/help - Прислать это сообщение\n'
        answer += '/minet - Делает приятно\n'
        answer += '/drakken - Присылает арт с Доктором Драккеном\n'
        answer += '/meme - Присылает мем\n'
        answer += '/art - Присылает картину\n'
        answer += '/breasts - Присылает грудь\n'
        answer += '/ass - Присылает задницу\n\n'
        answer += 'В чате мой функционал значительно шире'
    reply(message, answer, parse_mode='HTML')


def money_helper(message):
    answer = "<b>Финансовые команды:</b>\n\n"
    answer += "/money_off - Выключить финансовый режим\n\n"
    answer += '/money_on [Кол-во денег] - Включить финансовый режим с заданным бюджетом или обновить бюджет\n'
    answer += '[Казна] = [Кол-во денег] - [Деньги участников]\n'
    answer += 'Если кол-во денег не указано, будет установлена бесконечная казна\n\n'
    answer += '/m_emoji [Смайлик или короткий текст] - Поставить сокращение валюты\n'
    answer += '/m_name [Название] - Поставить название валюты\n'
    answer += 'Если она, к примеру называется доллар, пишите \n"/m_name долларов"\n\n'

    answer += '/top - Получить топ людей по валюте\n\n'

    answer += '/pay [Кол-во] - Заплатить челу. Если деньги не вечны, то берутся из казны. Забрать деньги тоже можно\n\n'

    answer += '/give [Кол-во] - Дать челу деньги из вашего личного счёта\n\n'

    # TODO answer += '/fund [Кол-во] - Заплатить в фонд чата'
    # TODO сбрасывалка денег чата
    reply(message, answer, parse_mode='HTML')


def minet(message, language):
    """Приносит удовольствие"""
    log.log_print(str(message.from_user.id) + ": minet invoked")
    if language:
        choices = []
        for i in minets[language].keys():
            choices.append(i)
        way = choice(choices)
        rep = choice(minets[language][way])
        if way == 'text':
            reply(message, rep)
        else:
            send_sticker(message.chat.id, rep, reply_to_message_id=message.message_id)


def send_stuff_from_storage(message, stuff):
    log.log_print("send_stuff_from_storage invoked")
    result = choice(get_list_from_storage(stuff))
    if result[1] == 'photo':
        send_photo(message.chat.id, result[0], reply_to_message_id=message.message_id, caption=result[2],
                   parse_mode='HTML')
    elif result[1] == 'video':
        send_video(message.chat.id, result[0], reply_to_message_id=message.message_id, caption=result[2],
                   parse_mode='HTML')
    elif result[1] == 'gif':
        send_document(message.chat.id, result[0], reply_to_message_id=message.message_id, caption=result[2],
                      parse_mode='HTML')
    else:
        reply(message, "Произошла ошибка!")


def send_meme(message):
    """Присылает мем"""
    log.log_print(str(message.from_user.id) + ": send_meme invoked")
    meme = choice(('AgADAgADx60xG2S_oUmVz41Dk8a4AkRNUw8ABAEAAwIAA20AAzj4BQABFgQ',
                   'AgADAgADdKsxG7PUsEmfWmu7wYQaSlHNuQ8ABAEAAwIAA20AA2gAAxYE',
                   'AgADAgAD-aoxG0EnIUqnHKx1l-EFFajiug8ABAEAAwIAA20AA3VUAAIWBA',
                   'AgADAgADY6sxG2RPyUmfTbFEJLvRV9Lhtw8ABAEAAwIAA20AA-lxAQABFgQ',
                   'AgADAgAD36sxG3h0uUlOXJnN-wooZiGxhQ8ABAEAAwIAA3gAA7nOAgABFgQ',
                   'AgADAgADJKsxG-KVuElBSmME_b_Cn8KghQ8ABAEAAwIAA20AA2DOAgABFgQ'))
    send_photo(message.chat.id, meme, reply_to_message_id=message.message_id)


def send_me(message, person):
    """Присылает человеку его запись в БД"""
    log.log_print(str(message.from_user.id) + ": send_me invoked")
    database = Database()
    system = database.get('chats', ('id', message.chat.id))['system']
    chat_config = get_system_configs(system)
    money_name = chat_config['money_name']
    member_update(system, person)  # Update person's messages, nickname and username
    p = get_person(person, system, database, system_configs=chat_config)
    appointments = [x['appointment'] for x in database.get_many('appointments', ('id', person.id), ('system', system))]
    if database.get('messages', ('person_id', person.id), ('chat_id', message.chat.id)):
        messages_here = database.get('messages', ('person_id', person.id), ('chat_id', message.chat.id))['messages']
    else:
        messages_here = 0
    msg = 'ID: {}\n'.format(p['id'])
    msg += 'Юзернейм: {}\n'.format(p['username'])
    msg += 'Никнейм: {}\n'.format(p['nickname'])
    msg += 'Ранг: {}\n'.format(p['rank'])
    msg += 'Кол-во сообщений в этом чате: {}\n'.format(messages_here)
    if p['messages']:
        msg += 'Кол-во сообщений во всей системе: {}\n'.format(p['messages'])
    msg += 'Кол-во предупреждений: {}\n'.format(p['warns'])
    if chat_config['money']:
        msg += 'Кол-во {}: {}\n'.format(money_name, p['money'])
    if appointments:
        msg += 'Должности: ' + ', '.join(appointments)
    reply(message, msg)


def send_some_top(message, language, format_string, start='', sort_key=lambda x: True, filter_f=lambda x: True,
                  to_private=True, reverse=True):
    # TODO Кто вышел из чата, а кто находится в чате
    log.log_print("send_some_top invoked")
    database = Database()
    # Declaring variables
    sent = False
    system = database.get('chats', ('id', message.chat.id))['system']
    bot_money = database.get('systems', ('id', system))['money']
    chat_configs = get_system_configs(system)
    emoji = chat_configs['money_emoji']
    text = start.format(bot_money=bot_money, m_emo=emoji)
    members = database.get_many('members', ('system', system))
    if to_private:
        target_chat = message.from_user.id
    else:
        target_chat = message.chat.id
    members = filter(lambda x: function_worked_correctly(sort_key, x), members)
    members = list(filter(lambda x: filter_f(x) and x['username'] != 'None', members))
    members.sort(key=sort_key, reverse=reverse)
    # Main loop
    # TODO если у челиков одинаковое значение сортировки, то они занимают несколько общих мест, например
    #  17—19. Новакид, Готлер, Генерал — 20 🍎
    for index in range(1, len(members)+1):
        member = members[index-1]
        p_link = link_text_wrapper(html_cleaner(member["nickname"]), f't.me/{member["username"]}')
        formating_dict = {'index': index, 'p_id': member['id'], 'p_link': p_link, 'messages': member['messages'],
                          'money': member['money'], 'm_emo': emoji, 'day': member['day_birthday']}
        if '{month}' in format_string:
            formating_dict['month'] = months_genitive[member['month_birthday']][language]
        text += format_string.format(**formating_dict)
        if index % 50 == 0:
            sent = send(target_chat, text, parse_mode='HTML', disable_web_page_preview=True)
            text = ''
    sent = send(target_chat, text, parse_mode='HTML', disable_web_page_preview=True) or sent
    if to_private:
        if sent:
            reply(message, "Выслал инфу в личку")
        else:
            reply(message, "Сначала запусти меня в личных сообщениях")
    elif not sent:
        reply(message, "Ничего нет!")


def money_give(message, person):
    """Функция обмена деньгами между людьми"""
    # TODO add nice link's to people instead of id's
    log.log_print(f"money_give invoked to person {person.id}")
    database = Database()
    getter = person.id
    giver = message.from_user.id
    money = message.text.split()[-1]
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    value_getter = database.get('members', ('id', getter), ('system', system))['money']
    value_giver = database.get('members', ('id', giver), ('system', system))['money']
    if money[0] == '-':
        reply(message, "Я вам запрещаю воровать")
    elif money == "0":
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
    else:
        money = int(money)
        if money > value_giver:
            reply(message, "Деньжат не хватает")
        else:
            value_getter += money
            value_giver -= money
            giv_m = send(giver, f"#Финансы\n\n Вы успешно перевели {money} денег на счёт {getter}. "
                                f"Теперь у вас их {value_giver}. А у него/неё {value_getter}")
            get_m = send(getter, f"#Финансы\n\n На ваш счёт было {money} денег со счёта {giver}. "
                                 f"Теперь у вас их {value_getter}. А у него/неё {value_giver}")
            if get_m:
                get_m = "🔔 уведомлён(а)"
            else:
                get_m = "🔕 не уведомлён(а)"
            if giv_m:
                giv_m = "🔔 уведомлён(а)"
            else:
                giv_m = "🔕 не уведомлён(а)"
            reply(message, f"#Финансы #Ф{getter} #Ф{giver}\n\n"
                           f"ID {getter} [{value_getter - money} --> {value_getter}] {get_m}\n"
                           f"ID {giver} [{value_giver + money} --> {value_giver}] {giv_m}\n")
            send(admin_place(message, database), f"#Финансы #Ф{getter} #Ф{giver}\n\n"
                                                 f"ID {getter} [{value_getter - money} --> {value_getter}] {get_m}\n"
                                                 f"ID {giver} [{value_giver + money} --> {value_giver}] {giv_m}\n")
    database.change(value_getter, 'money', 'members', ('id', getter), ('system', system))
    database.change(value_giver, 'money', 'members', ('id', giver), ('system', system))


# TODO More comfortable way to insert birthday
def month_set(message, month):
    log.log_print(f"month_set invoked")
    database = Database()
    reply(message, "Ставлю человеку с ID {} месяц рождения {}".format(message.from_user.id, month))
    database.change(month, 'month_birthday', 'members', ('id', message.from_user.id))


def day_set(message, day, language):
    log.log_print(f"day_set invoked")
    days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    database = Database()
    month = database.get('members', ('id', message.from_user.id))['month_birthday']
    if not month:
        reply(message, "Сначала поставь месяц рождения")
    elif day > days[month - 1]:
        month = months_prepositional[month][language]
        reply(message, "В {} нет столько дней".format(month.lower()))
    else:
        reply(message, "Ставлю человеку с ID {} день рождения {}".format(message.from_user.id, day))
        database.change(day, 'day_birthday', 'members', ('id', message.from_user.id))


def admins(message):
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
        admins_id = [admin['id'] for admin in database.get_many('appointments', ('appointment', boss))]
        admins_username = ['@' + database.get('members', ('id', admin), ('system', system))['username'] for admin in
                           admins_id]
    reply(message, 'Вызываю сюда админов: ' + ', '.join(admins_username))


def chats(message):
    database = Database()
    chats_list = database.get_many('chats', ('type', 'public'))

    # Получаем имена и ссылки нужных нам чатиков
    chats_names = [chat['name'] for chat in chats_list]
    chats_links = ['@' + chat['link'] for chat in chats_list]

    # Генерируем текст для отображение имен и ссылок вместе
    text = '\n'.join([f'{key}: {value}' for key, value in zip(chats_names, chats_links)])
    reply(message, text)


def chat_check(message):
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
    # properties = ['id', 'name', 'purpose', 'type', 'link', 'standart_commands', 'boss_commands', 'financial_commands',
    #              'mutual_invites', 'messages_count', 'violators_ban', 'admins_promote']
    text = 'Настройки этого чата:\n\n'
    for feature in features:
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
            text += f"{features_texts['Russian'][features.index(feature)]}: \n{mark} {microtext}\n"
            if '⚙' in mark or '❌' in mark:
                text += f"/{feature}_on Включить на постоянку\n"
            if '⚙' in mark or '✅' in mark:
                text += f"/{feature}_off Выключить на постоянку\n"
            if '⚙' not in mark:
                text += f"/{feature}_default Поставить значение по умолчанию\n"
            text += '\n'
    reply(message, text)


def system_check(message):
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = database.get('systems', ('id', chat['system']))
    print(system)
    text = 'Настройки по умолчанию:\n\n'
    for feature in features:
        system_property = system[feature]
        if system_property == 2:
            text += f"{features_texts['Russian'][features.index(feature)]}: \n✅ Включено\n"
            text += f"/s_{feature}_off Выключить\n\n"
        elif system_property == 1:
            text += f"{features_texts['Russian'][features.index(feature)]}: \n❌ Выключено\n"
            text += f"/s_{feature}_on Включить\n\n"
    reply(message, text)


def anon_message(message):
    log.log_print('anon_message invoked')
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
        text = "Вижу вы сидите в нескольких чатах. Чтобы уточнить, в какой админосостав отправлять сообщение, " \
               "оформите вашу команду так:\n\n/anon <номер системы> <ваше послание>.\n\n Вот список систем:\n"
        names = [f"{sys} — {data[sys]['name']}" for sys in systems]
        reply(message, text + '\n'.join(names))
    if system:
        system_entry = database.get('systems', ('id', system))
        if system_entry:
            if system_entry['admin_place']:
                anon_message_text = ' '.join(message.text.split()[1:])
                sent = send(system_entry['admin_place'], "#anon\n\n" + anon_message_text[system_specification_length:])
                if sent:
                    reply(message, "Сообщение успешно отправлено. Спасибо за ваше мнение!")
                else:
                    reply(message, "Произошла ошибка!")
            else:
                reply(message, "У этой системы админосостав не отмечен")
        else:
            reply(message, "Этой системы не существует!")
