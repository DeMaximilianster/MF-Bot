# -*- coding: utf-8 -*-
"""This is a module for commands without inline-buttons,
and that require some special ranks
"""
from time import time

from presenter.config.database_lib import Database
from presenter.config.config_var import full_chat_list, channel_list, BOT_ID, \
    admin_place, chat_list, CREATOR_ID, ORIGINAL_TO_ENGLISH, ENGLISH_TO_ORIGINAL
from presenter.config.log import Logger, LOG_TO
from presenter.config.config_func import unban_user, is_suitable, \
    get_system_configs, photo_video_gif_get, get_target_message, \
    update_systems_json, create_chat, SystemUpdate, \
    write_storage_json, get_storage_json, get_person, person_link, \
    person_info_in_html, chat_info_in_html
import presenter.config.config_func as cf
from presenter.config.languages import get_word_object
from view.output import kick, reply, promote, send, forward, restrict

LOG = Logger(LOG_TO)


@LOG.wrap
def language_setter(message):
    """Sets the language of the chat"""
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


@LOG.wrap
def add_stuff_to_storage(message, storage_name):
    """Add some media to media storage"""
    rep = message.reply_to_message
    storages_dict = get_storage_json()
    if rep:
        insert = photo_video_gif_get(rep)
        if insert:
            if list(insert) in storages_dict[storage_name]['contents']:
                reply(message, "У меня это уже есть)")
            else:
                storages_dict[storage_name]['contents'].append(insert)
                forward(CREATOR_ID, message.chat.id, rep.message_id)
                send(CREATOR_ID, f"Норм контент?) user={message.from_user.id}, "
                     f"text={message.text}, id=<code>{insert[0]}</code>",
                     parse_mode='HTML')
                write_storage_json(storages_dict)
                reply(message, "ОК!")
        else:
            reply(message, "Ответить надо на гифку, фотографию или видео")
    else:
        reply(message, "Надо ответить на медиа, которое нужно добавить")


@LOG.wrap
def remove_stuff_from_storage(message, storage_name, file_id):
    """Removes some media from media storage"""
    storages_dict = get_storage_json()
    storage = storages_dict[storage_name]
    for index in range(len(storage['contents'])):
        if file_id == storage['contents'][index][0]:
            storages_dict[storage_name]['contents'].pop(index)
            write_storage_json(storages_dict)
            reply(message, "ОК!")
            break
    else:
        reply(message, "Не вижу такого в хранилище")


@LOG.wrap
def create_new_storage(message, storage_mame, is_vulgar):
    """ Creates new media storage """
    storages_dict = get_storage_json()
    if storage_mame not in storages_dict.keys():
        new_storage = {'is_vulgar': is_vulgar, 'moders': [CREATOR_ID], 'contents': []}
        storages_dict[storage_mame] = new_storage
        write_storage_json(storages_dict)
        vulgar_text = ' вульгарное' if is_vulgar else ''
        reply(message, "Созданное новое{} хранилище {}".format(vulgar_text, storage_mame))
    else:
        reply(message, "Такое хранилище уже есть")


@LOG.wrap
def add_moderator_to_storage(message, storage_name, person_id):
    """ Adds a moderator to a storage """
    storages_dict = get_storage_json()
    if person_id not in storages_dict[storage_name]['moders']:
        storages_dict[storage_name]['moders'].append(person_id)
        write_storage_json(storages_dict)
        reply(message, "ОК!")
    else:
        reply(message, "Этот человек уже модератор хранилища")


@LOG.wrap
def remove_moderator_from_storage(message, storage_name, person_id):
    """ Removes a moderator from a storage """
    storages_dict = get_storage_json()
    if person_id in storages_dict[storage_name]['moders']:
        storages_dict[storage_name]['moders'].remove(person_id)
        write_storage_json(storages_dict)
        reply(message, "ОК!")
    else:
        reply(message, "Этот человек и так не модератор хранилища")


@LOG.wrap
def update_all_members(message):
    """Updates all the messages, usernames and nicknames"""
    sent = reply(message, "Начинаю обновление...")
    database = Database(to_log=False)
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    members = list(database.get_many('members', ('system', system)))
    system_update = SystemUpdate(message.chat.id, system, members, sent)
    system_update.start()


@LOG.wrap
def warn(message, person, parameters_dictionary):
    """Даёт участнику предупреждение"""
    database = Database()
    warns = parameters_dictionary['value']
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    value = database.get('members', ('id', person.id), ('system', system))['warns'] + warns
    database.change(value, 'warns', 'members', ('id', person.id), ('system', system))
    reply(message, "Варн(ы) выдан(ы). Теперь их {}".format(value))
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} получил(а) {} варн(а) и их стало {}".format(
            person_info_in_html(person), warns, value), parse_mode='HTML')
    blowout = database.get('channels', ('name', 'Проколы'))['id']
    how_many = 10  # Сколько пересылает сообщений
    end_forwarding = message.reply_to_message.message_id
    start_forwarding = end_forwarding - how_many
    send(blowout, "В чате {} случилось нарушение участником {} Прысылаю {} сообщений".
         format(chat_info_in_html(message.chat), person_info_in_html(person), how_many),
         parse_mode='HTML')
    for msg_id in range(start_forwarding, end_forwarding + 1):
        forward(blowout, message.chat.id, msg_id)
    if value >= 3:
        ban(message, person)


@LOG.wrap
def unwarn(message, person, parameters_dictionary: dict):
    """Снимает с участника предупреждение"""
    database = Database()
    unwarns = parameters_dictionary['value']
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    value = database.get('members', ('id', person.id), ('system', system))['warns'] - unwarns
    if value >= 0:
        database.change(value, 'warns', 'members', ('id', person.id), ('system', system))
        adm_place = admin_place(message, database)
        if adm_place:
            text = "#warns\n\n"
            text += "Пользователь {} потерял(а) {} варн(а) и их стало {}\n".format(
                person_info_in_html(person), unwarns, value)
            text += "Варн(ы) снят(ы) пользователем {}\n".format(person_info_in_html(
                message.from_user))
            if 'comment' in parameters_dictionary.keys():
                text += "Комментарий: {}".format(parameters_dictionary['comment'])
            send(adm_place, text, parse_mode='HTML')
        reply(message, "Варн(ы) снят(ы). Теперь их {}".format(value))
        if 3 - unwarns <= value < 3:
            chat_configs = get_system_configs(system)
            unban_user(person)
            database.change(chat_configs['ranks'][1], 'rank', 'members',
                            ('id', person.id), ('system', system))
    else:
        reply(message, "Нельзя сделать отрицательное количество предупреждений")


@LOG.wrap
def ban(message, person, comment=True, unban_then=False):
    """Даёт участнику бан"""
    database = Database()
    blowout = database.get('channels', ('name', 'Проколы'))['id']
    how_many = 3  # Сколько пересылает сообщений
    if not unban_then:
        end_forwarding = get_target_message(message).message_id
        start_forwarding = end_forwarding - how_many
        send(blowout, "В чате {} забанили участника {}. Прысылаю {} сообщений".
             format(chat_info_in_html(message.chat), person_info_in_html(person), how_many),
             parse_mode='HTML')
        for msg_id in range(start_forwarding, end_forwarding + 1):
            forward(blowout, message.chat.id, msg_id)
    if comment:
        send(message.chat.id, "Ну всё, этому челу " + "бан" * (not unban_then) + "кик" * unban_then)
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    chat_configs = get_system_configs(system)
    if not unban_then:
        database.change(chat_configs['ranks'][0], 'rank', 'members',
                        ('id', person.id), ('system', system))
    for chat in full_chat_list(database, system):
        kick(chat['id'], person.id)
    for channel in channel_list(database):
        kick(channel['id'], person.id)
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} получил(а) бан".format(
            person_info_in_html(person) + ', но сразу и разбан' * unban_then), parse_mode='HTML')
    if unban_then:
        unban_user(person)


@LOG.wrap
def mute(message, person, parameters_dictionary):
    """Даёт участнику бан"""
    database = Database()
    hours = parameters_dictionary['value']
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    for chat in full_chat_list(database, system):
        restrict(chat['id'], person.id, until_date=time() + hours * 3600)
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} получил(а) мут на {} час(ов)".format(
            person_info_in_html(person), hours), parse_mode='HTML')
    reply(message, "Мут выдан")


def money_pay(message, person, parameters_dictionary):
    """Платит человеку деньги из бюджета чата"""
    LOG.log(f"money pay invoked to person {person.id}")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    bot_money = database.get('systems', ('id', system))['money']
    if bot_money != 'inf':
        bot_money = int(bot_money)
    p_id = person.id
    money = parameters_dictionary['value']
    money_name_word = get_word_object(get_system_configs(system)['money_name'], 'Russian')
    money_name = money_name_word.cased_by_number(abs(money), if_one_then_accusative=True)
    person_money = get_person(message, person, system, database)['money']
    if money == 0:
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
    elif money < 0:
        money = -int(money)  # Делаем из отрицательного числа положительное
        if person_money - money >= 0:
            person_money -= money
            if bot_money != 'inf':
                bot_money += money
            sent = send(p_id, "#Финансы\n\n"
                              f"С вашего счёта было снято {money} {money_name} в банк. "
                              f"Теперь у вас {person_money}")
            sent = cf.value_marker(sent, "🔔 уведомлён(а)", "🔕 не уведомлён(а)")
            reply(message,
                  'У {} забрали {} {} в банк!'.format(person_link(person), money, money_name),
                  parse_mode='HTML')
            answer = "#Финансы " + f"#f{p_id}\n\n"
            if bot_money != 'inf':
                answer += f"#Бюджет [{bot_money - money} --> {bot_money}]\n"
            answer += f"{person_link(person)} [{person_money + money} --> {person_money}] {sent}"
            send(admin_place(message, database), answer, parse_mode='HTML')
        else:
            reply(message,
                  "У людей число {} должно быть больше нуля".format(
                      money_name_word.genitive_plural()))
    else:
        if bot_money != 'inf' and bot_money < money:
            reply(message, "У нас нет столько {} в банке".format(money_name_word.genitive_plural()))
        else:
            person_money += money
            sent = send(p_id, "#Финансы\n\n"
                              f"На ваш счёт было переведено {money} {money_name} из банка. "
                              f"Теперь у вас {person_money}")
            sent = cf.value_marker(sent, "🔔 уведомлён(а)", "🔕 не уведомлён(а)")
            reply(message,
                  '{} получил(а) из банка {} {}!'.format(person_link(person), money, money_name),
                  parse_mode='HTML')
            answer = "#Финансы " + f"#f{p_id}\n\n"
            if bot_money != 'inf':
                bot_money -= money
                answer += f"#Бюджет [{bot_money + money} --> {bot_money}]\n"
            answer += f"{person_link(person)} [{person_money - money} --> {person_money}] {sent}"
            send(admin_place(message, database), answer, parse_mode='HTML')
    database.change(person_money, 'money', 'members', ('id', p_id), ('system', system))
    if bot_money != 'inf':
        database.change(bot_money, 'money', 'systems', ('id', system))


def money_reset(message):
    """Take all users' money to a system fund"""
    database = Database()
    system = database.get('chats', ('id', message.chat.id))['system']
    system_money = database.get('systems', ('id', system))['money']
    members = database.get_many('members', ('system', system))

    # Get the amount of money of chat members
    members_money = sum([member['money'] for member in members])
    if system_money != 'inf':
        database.increase(members_money, 'money', 'systems', ('id', system))
    database.change(0, 'money', 'members', ('system', system))
    reply(message, "OK")


@LOG.wrap
def give_admin(message, person, loud=True):
    """Назначает человека админом"""
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list(database, system):
        promote(chat['id'], person.id,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
    for channel in channel_list(database):
        promote(channel['id'], person.id, can_post_messages=True, can_invite_users=True)
    if loud:
        reply(message, "Теперь это админ!")


@LOG.wrap
def del_admin(message, person, loud=True):
    """Remove admin's right"""
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    database.remove("appointments", ("appointment", "Admin"), ("id", person.id))
    for chat in chat_list(database, system):
        promote(chat['id'], person.id,
                can_change_info=False, can_delete_messages=False, can_invite_users=False,
                can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
    for channel in channel_list(database):
        promote(channel['id'], person.id, can_post_messages=False, can_invite_users=False)
    if loud:
        reply(message, "Теперь это не админ!")


@LOG.wrap
def rank_changer(message, person):
    """Changes person's rank"""
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    chat_configs = get_system_configs(system)
    command = message.text.split()[0].split(sep='@')[0]
    adm_place = admin_place(message, database)
    if command in chat_configs["ranks_commands"]:
        rank_index = chat_configs["ranks_commands"].index(command)
        rank = chat_configs["ranks"][rank_index]
        database.change(rank, "rank", 'members', ('id', person.id), ('system', system))
        reply(message, f"Теперь это {rank} по званию!")
        if adm_place:
            send(adm_place, "Пользователь {} получил(а) звание {}".format(
                person_info_in_html(person), rank), parse_mode='HTML')
    elif command in chat_configs["appointment_adders"]:
        appointment_index = chat_configs["appointment_adders"].index(command)
        appointment = chat_configs["appointments"][appointment_index]
        if not database.get('appointments', ('id', person.id), ('system', system),
                            ('appointment', appointment)):
            database.append((person.id, system, appointment), "appointments")
            reply(message, f"Теперь это {appointment}. Поздравим человека с повышением!")
            if adm_place:
                send(adm_place, "Пользователь {} получил(а) должность {}".format(
                    person_info_in_html(person), appointment), parse_mode='HTML')
        else:
            reply(message, "У этого человека и так есть эта должность")
    elif command in chat_configs["appointment_removers"]:
        appointment_index = chat_configs["appointment_removers"].index(command)
        appointment = chat_configs["appointments"][appointment_index]
        database.remove("appointments", ('id', person.id), ('system', system),
                        ('appointment', appointment))
        reply(message, f"Теперь это не {appointment}")
        if adm_place:
            send(adm_place, "Пользователь {} потерял(а) должность {}".format(
                person_info_in_html(person), appointment), parse_mode='HTML')
    unban_user(person)
    if is_suitable(message, person, 'boss', loud=False):
        give_admin(message, person, loud=False)
    else:
        del_admin(message, person, loud=False)


def message_change(message, person, parameters_dictionary):
    """Меняет запись в БД о количестве сообщений чела"""
    LOG.log(f"message_change invoked to person {person.id}")
    database = Database()
    p_id = person.id
    ch_id = message.chat.id
    value = parameters_dictionary['value']
    reply(message, "Ставлю этому человеку в этот чат количество сообщений {}".format(value))
    if not database.get('messages', ('person_id', p_id), ('chat_id', ch_id)):
        database.append((p_id, ch_id, value), 'messages')
    else:
        database.change(value, 'messages', 'messages', ('person_id', p_id), ('chat_id', ch_id))


@LOG.wrap
def deleter_mode(message):
    """Удалять медиа или нет"""
    database = Database()
    delete = int(database.get('config', ('var', 'delete'))['value'])
    delete = (delete + 1) % 2  # Переводит 0 в 1, а 1 в 0
    database.change(delete, 'value', 'config', ('var', 'delete'))
    if delete:
        reply(message, 'Окей, господин, теперь я буду удалять медиа, которые присланы гостями')
    else:
        reply(message, 'Окей, гости могут спокойной слать свои медиа')


@LOG.wrap
def add_chat(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    database = Database()
    system = None
    message_words = message.text.split()
    if len(message_words) == 2:
        system = message_words[-1]
    chat_type, link = cf.get_chat_type_and_chat_link(message.chat)
    if database.get('chats', ('id', message.chat.id)):
        reply(message, "Этот чат уже записан")
    elif system:  # system is specified
        if database.get('systems', ('id', system)):  # Adding new chat to existing system
            if database.get('members', ('id', message.from_user.id), ('system', system)):
                if is_suitable(message, message.from_user, "chat_changer", system=system):
                    create_chat(message, system, chat_type, link, database)
                    reply(message, "Теперь я здесь работаю! "
                                   "Вы можете менять настройки по умолчанию в /system, "
                                   "так что чтобы поменять настройки везде, вам не надо "
                                   "в каждом чате лезть в /chat")
                else:
                    reply(message,
                          "У вас в этой системе нет полномочий для добавления чатов в неё)")
            else:
                reply(message, "Произошла ошибка!")
        else:
            reply(message, "Такой системы не существует")
    else:
        reply(message, "Пожалуйста укажите номер системы после команды")


@LOG.wrap
def del_chat(message):
    """Removes chat from the system."""
    chat = message.chat.id
    database = Database()

    if database.get('chats', ('id', chat)):
        database.remove('chats', ('id', chat))
        reply(message, "Чат успешно удалён")


@LOG.wrap
def add_admin_place(message):
    """Add admin place to system"""
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    if chat:
        system = chat["system"]
        database.change(message.chat.id, "admin_place", "systems", ('id', system))
        reply(message, "Теперь это чат админов. Я сюда буду присылать различные уведомления!")
    else:
        reply(message, "Произошла ошибка!")


@LOG.wrap
def chat_options(message):
    """Optimize current chat"""
    database = Database()
    text = message.text.split(sep='@')[0]
    last_word = text.split(sep='_')[-1]
    if last_word == 'default':
        mode = 2
        text = text[1:-8]
    elif last_word == 'on':
        mode = 1
        text = text[1:-3]
    else:  # last_word == 'off'
        mode = 0
        text = text[1:-4]
    database.change(mode, text, 'chats', ('id', message.chat.id))
    reply(message, "ОК!")


@LOG.wrap
def system_options(message):
    """Optimize current system"""
    database = Database()
    text = message.text.split(sep='@')[0]
    last_word = text.split(sep='_')[-1]
    if last_word == 'on':
        mode = 2
        text = text[3:-3]
    else:  # last_word == 'off'
        mode = 1
        text = text[3:-4]
    system = database.get('chats', ('id', message.chat.id))['system']
    database.change(mode, text, 'systems', ('id', system))
    reply(message, "ОК!")


@LOG.wrap
def money_mode_change(message):
    """Change the money mode in system. Infinite, finite or no money"""
    database = Database()

    mode = message.text.split()[0].split(sep='@')[0].split(sep='_')[-1]

    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    update_systems_json(system, mode == 'on', 'money')
    if mode == 'on':
        all_money = message.text.split()[-1]
        if all_money.isdecimal():
            all_money = int(all_money)
            people = list(database.get_many('members', ('system', system)))
            people = list(filter(lambda x: x['money'] != 0 and x['id'] != BOT_ID, people))
            money = 0
            for person in people:
                money += person['money']
            all_money -= money
            if all_money < 0:
                reply(message, "Казна выходит отрицательная, ставлю бесконечную валюту")
                database.change('inf', 'money', 'systems', ('id', system))
            else:
                reply(message, f"В казне выходит {all_money} денег. Спасибо за сотрудничество!")
                database.change(all_money, 'money', 'systems', ('id', system))
        else:
            database.change('inf', 'money', 'systems', ('id', system))
            reply(message, "Бесконечная валюта поставлена")
    else:
        reply(message, "Валюта выключена")


@LOG.wrap
def money_emoji(message):
    """Change money's emoji in json"""
    database = Database()
    mode = ' '.join(message.text.split()[1:])
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    if len(mode) > 10:
        reply(message, "Смайлик-сокращение валюты не должен превышать 10 символов")
    elif mode:
        update_systems_json(system, mode, 'money_emoji')
        reply(message, "OK!")
    else:
        reply(message, "После команды введите смайлик-сокращение валюты")


@LOG.wrap
def set_money_name(message):
    """Change money's name in json"""
    database = Database()
    mode = ' '.join(message.text.split()[1:])
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    if mode:
        update_systems_json(system, mode, 'money_name')
        reply(message, "OK!")
    else:
        reply(message, "После команды введите название валюты")


def update_greetings_json(message, which_greeting: str):
    """Changes greetings in some system"""
    database = Database()
    data = cf.get_systems_json()
    system = database.get('chats', ('id', message.chat.id))['system']
    system_configs = data[system]
    text = cf.entities_saver(message.text, message.entities)
    text = ' '.join(text.split()[1:])
    system_configs['greetings'][which_greeting] = text
    data[system] = system_configs
    cf.write_systems_json(data)
    reply(message, 'Поставлен текст: "{}"'.format(text), parse_mode='HTML')
