# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from presenter.config.config_var import full_chat_list, channel_list, bot_id, admin_place, chat_list
from presenter.config.log import Loger, log_to
from presenter.config.config_func import unban_user, is_suitable
from view.output import kick, reply, promote, send, forward, restrict
import json
from presenter.config.files_paths import systems_file
from time import time

work = True
log = Loger(log_to)

# TODO команда /kick, кикает и сразу разбанивает

# TODO команда для делания гражданином, высшим гражданином
# TODO команда для делания Членом Комитета
# TODO сделать сменяемого зама автоматически (команда /vice)


def warn(message, person):
    """Даёт участнику предупреждение"""
    log.log_print("warn invoked")
    database = Database()
    if len(message.text.split()) > 1:
        warns = int(message.text.split()[-1])  # TODO Эта проверка происходит дважды
    else:
        warns = 1
    if warns == 0:
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
        return None
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    value = database.get('members', ('id', person.id), ('system', system))['warns'] + warns
    database.change(value, 'warns', 'members', ('id', person.id), ('system', system))
    reply(message, "Варн(ы) выдан(ы). Теперь их {}".format(value))
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} (@{}) [{}] получил(а) {} варн(а) и их стало {}".format(
        person.first_name, person.username, person.id, warns, value))
    blowout = database.get('channels', ('name', 'Проколы'))['id']
    how_many = 10  # Сколько пересылает сообщений
    end_forwarding = message.reply_to_message.message_id
    start_forwarding = end_forwarding - how_many
    send(blowout, "В чате '{}' случилось нарушение участником {} (@{}) [{}]. Прысылаю {} сообщений".
         format(message.chat.title, person.first_name, person.username, person.id, how_many))
    for msg_id in range(start_forwarding, end_forwarding + 1):
        forward(blowout, message.chat.id, msg_id)
    if value >= 3:
        ban(message, person)


def unwarn(message, person):
    """Снимает с участника предупреждение"""
    log.log_print("unwarn invoked")
    database = Database()
    if len(message.text.split()) > 1:
        unwarns = int(message.text.split()[-1])  # TODO Эта проверка происходит дважды
    else:
        unwarns = 1
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    value = database.get('members', ('id', person.id), ('system', system))['warns'] - unwarns
    database.change(value, 'warns', 'members', ('id', person.id), ('system', system))
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} (@{}) [{}] получил(а) {} варн(а) и их стало {}".format(
        person.first_name, person.username, person.id, unwarns, value))
    reply(message, "Варн(ы) снят(ы). Теперь их {}".format(value))
    if 3 - unwarns <= value < 3:
        read_file = open(systems_file, 'r', encoding='utf-8')
        data = json.load(read_file)
        read_file.close()
        chat_configs = data[system]
        database.change(chat_configs['ranks'][0], 'rank', 'members', ('id', person.id), ('system', system))


def ban(message, person, comment=True, unban_then=False):
    """Даёт участнику бан"""
    log.log_print("ban invoked")
    database = Database()
    blowout = database.get('channels', ('name', 'Проколы'))['id']
    how_many = 3  # Сколько пересылает сообщений
    target = message
    if message.reply_to_message:
        target = message.reply_to_message
    end_forwarding = target.message_id
    start_forwarding = end_forwarding - how_many
    send(blowout, "В чате '{}' забанили участника {} (@{}) [{}]. Прысылаю {} сообщений".
         format(message.chat.title, person.first_name, person.username, person.id, how_many))
    for msg_id in range(start_forwarding, end_forwarding + 1):
        forward(blowout, message.chat.id, msg_id)
    if comment:
        send(message.chat.id, "Ну всё, этому челу бан")
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    read_file = open(systems_file, 'r', encoding='utf-8')
    data = json.load(read_file)
    read_file.close()
    chat_configs = data[system]
    if not unban_then:
        database.change(chat_configs['ranks'][0], 'rank', 'members', ('id', person.id), ('system', system))
    for chat in full_chat_list(database, system):
        kick(chat['id'], person.id)
    for channel in channel_list(database):
        kick(channel['id'], person.id)
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} (@{}) [{}] получил(а) бан".format(
            person.first_name, person.username, person.id)+', но сразу и разбан'*unban_then)
    if unban_then:
        unban_user(person)


def mute(message, person):
    """Даёт участнику бан"""
    log.log_print("mute invoked")
    database = Database()
    hours = int(message.text.split()[-1])
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    for chat in full_chat_list(database, system):
        restrict(chat['id'], person.id, until_date=time()+hours*3600)
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} (@{}) [{}] получил(а) мут на {} час(ов)".format(
            person.first_name, person.username, person.id, hours))


def money_pay(message, person):
    """Платит человеку деньги из бюджета чата"""
    # TODO Добавить уведомление о человеке, совершившем перевод
    # TODO add nice link's to people instead of id's
    log.log_print(f"money pay invoked to person {person.id}")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    bot_money = int(database.get('systems', ('id', system))['money'])
    p_id = person.id
    money = message.text.split()[-1]
    value = database.get('members', ('id', p_id), ('system', system))['money']
    if money == "0":
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
    elif money[0] == '-':
        money = -int(money)  # Делаем из отрицательного числа положительное
        if value - money >= 0:
            value -= money
            bot_money += money
            sent = send(p_id, f"#Финансы\n\n"
                              f"С вашего счёта было снято {money} ЯМ в фонд чата. У вас осталось {value} ЯМ")
            if sent:
                sent = "🔔 уведомлён(а)"
            else:
                sent = "🔕 не уведомлён(а)"
            reply(message, f"#Финансы #Бюджет #Ф{p_id}\n\n"
                           f"Бюджет [{bot_money - money} --> {bot_money}]\n"
                           f"ID {p_id} [{value + money} --> {value}] {sent}")
            send(admin_place(message, database), f"#Финансы #Бюджет #Ф{p_id}\n\n"
                                        f"Бюджет [{bot_money - money} --> {bot_money}]\n"
                                        f"ID {p_id} [{value + money} --> {value}] {sent}")
        else:
            reply(message, "Часто у людей видишь отрицательное количество денег?")
    else:
        money = int(money)
        if bot_money < money:
            reply(message, "У нас нет столько в бюджете")
        else:
            value += money
            bot_money -= money
            sent = send(p_id, f"#Финансы\n\n"
                              f"На ваш счёт было переведено {money} ЯМ из фонда чата. Теперь у вас {value} ЯМ")
            if sent:
                sent = "🔔 уведомлён(а)"
            else:
                sent = "🔕 не уведомлён(а)"
            reply(message, f"#Финансы #Бюджет #Ф{p_id}\n\n"
                           f"Бюджет [{bot_money + money} --> {bot_money}]\n"
                           f"ID {p_id} [{value - money} --> {value}] {sent}")

            send(admin_place(message, database), f"#Финансы #Бюджет #Ф{p_id}\n\n"
                                        f"Бюджет [{bot_money + money} --> {bot_money}]\n"
                                        f"ID {p_id} [{value - money} --> {value}] {sent}")
    database.change(value, 'money', 'members', ('id', p_id), ('system', system))
    database.change(bot_money, 'money', 'systems', ('id', system))
    # TODO Засунуть эти зассанские уебанские денежные функции в отдельный блять модуль


def give_admin(message, person, loud=True):
    """Назначает человека админом"""
    log.log_print("give_admin invoked")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    # TODO При повторном использовании команды не должна появляться новая запись
    database.append((person.id, "Admin"), table='appointments')
    # TODO пусть бот шлёт админу ссылку на чат админосостава и меняет её при входе
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list(database, system):
        promote(chat['id'], person.id,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
    for channel in channel_list(database):
        promote(channel['id'], person.id, can_change_info=True, can_post_messages=True, can_invite_users=True)
    if loud:
        reply(message, "Теперь это админ!")


def del_admin(message, person, loud=True):
    log.log_print("del_admin invoked")
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


def rank_changer(message, person):
    """Changes person's rank"""
    log.log_print(f"{__name__} invoked")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    read_file = open(systems_file, 'r', encoding='utf-8')
    data = json.load(read_file)
    read_file.close()
    chat_configs = data[str(system)]
    command = message.text.split()[0]
    adm_place = admin_place(message, database)

    if command in chat_configs["ranks_commands"]:
        rank_index = chat_configs["ranks_commands"].index(command)
        rank = chat_configs["ranks"][rank_index]
        database.change(rank, "rank", 'members', ('id', person.id), ('system', system))
        reply(message, f"Теперь это {rank} по званию!")
        if adm_place:
            send(adm_place, "Пользователь {} (@{}) [{}] получил(а) звание {}".format(
                person.first_name, person.username, person.id, rank))
    elif command in chat_configs["appointment_adders"]:
        appointment_index = chat_configs["appointment_adders"].index(command)
        appointment = chat_configs["appointments"][appointment_index]
        database.append((person.id, system, appointment), "appointments")
        reply(message, f"Теперь это {appointment}. Поздравим человека с назначением на должность!")
        if adm_place:
            send(adm_place, "Пользователь {} (@{}) [{}] получил(а) должность {}".format(
                person.first_name, person.username, person.id, appointment))
    elif command in chat_configs["appointment_removers"]:
        appointment_index = chat_configs["appointment_removers"].index(command)
        appointment = chat_configs["appointments"][appointment_index]
        database.remove("appointments", ('id', person.id), ('system', system), ('appointment', appointment))
        reply(message, f"Теперь это не {appointment}")
        if adm_place:
            send(adm_place, "Пользователь {} (@{}) [{}] потерял(а) должность {}".format(
                person.first_name, person.username, person.id, appointment))
    unban_user(person)
    if is_suitable(message, person, 'boss', loud=False):
        give_admin(message, person, loud=False)
    else:
        del_admin(message, person, loud=False)


def message_change(message, person):
    """Меняет запись в БД о количестве сообщений чела"""
    log.log_print(f"message_change invoked to person {person.id}")
    database = Database()
    p_id = person.id
    ch_id = message.chat.id
    messages = message.text.split()[-1]
    value = int(messages)
    reply(message, "Ставлю человеку с ID {} в чат с ID {} количество сообщений равное {}".format(p_id, ch_id, value))
    if not database.get('messages', ('person_id', p_id), ('chat_id', ch_id)):
        database.append((p_id, ch_id, value), 'messages')
    else:
        database.change(value, 'messages', 'messages', ('person_id', p_id), ('chat_id', ch_id))


def deleter_mode(message):
    """Удалять медиа или нет"""
    log.log_print("deleter_mode invoked")
    database = Database()
    delete = int(database.get('config', ('var', 'delete'))['value'])
    delete = (delete + 1) % 2  # Переводит 0 в 1, а 1 в 0
    database.change(delete, 'value', 'config', ('var', 'delete'))

    if delete:
        reply(message, 'Окей, господин, теперь я буду удалять медиа, которые присланы гостями')
    else:
        reply(message, 'Окей, гости могут спокойной слать свои медиа')


def add_chat(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    # TODO Предохранитель на уникальность некоторых чатов
    log.log_print("add_chat invoked")
    database = Database()
    system = None
    message_words = message.text.split()
    if len(message_words) == 2:
        system = message_words[-1]
    typee = 'private'
    link = 'None'
    if message.chat.username:
        typee = 'public'
        link = message.chat.username
    if database.get('chats', ('id', message.chat.id)):
        reply(message, "Этот чат уже записан")
    elif system:
        if database.get('systems', ('id', system)):  # Adding new chat to existing system
            if database.get('members', ('id', message.from_user.id), ('system', system)):
                if is_suitable(message, message.from_user, "chat_changer", system=system):
                    chat = (message.chat.id, system, message.chat.title, typee, link, 2, 2, 2, 2, 2, 2, 2)
                    database.append(chat, 'chats')
                    reply(message, "Теперь я здесь работаю!")
            else:
                reply(message, "У вас в этой системе нет полномочий для добавления чатов в неё)")
        else:
            reply(message, "Такой системы не существует")
    elif message.from_user.id in [381279599]:  # Creating new system if adder is an MF diplomate
        all_systems = database.get_all('systems', 'id')
        ids = [int(sys['id']) for sys in all_systems]
        new_id = str(max(ids) + 1)
        database.append((message.chat.id, new_id, message.chat.title, typee, link, 2, 2, 2, 2, 2, 2, 2), 'chats')
        database.append((new_id, 0, 0, 0, 1, 0, 0, 2, 1, 1), 'systems')
        read_file = open(systems_file, 'r', encoding='utf-8')
        data = json.load(read_file)
        read_file.close()
        data[new_id] = {"name": message.chat.title, "money": False,
                        "ranks": ["Забаненный", "Участник", "Админ", "Старший Админ", "Лидер"],
                        "ranks_commands": [None, "/guest", "/admin", "/senior_admin", "/leader"],
                        "appointments": [],
                        "appointment_adders": [],
                        "appointment_removers": [],
                        "commands": {"standart": ["Участник", "Лидер"],
                                     "advanced": ["Участник", "Лидер"],
                                     "boss": ["Админ", "Лидер"],
                                     "uber": ["Старший Админ", "Лидер"],
                                     "chat_changer": ["Лидер", "Лидер"]}}
        write_file = open(systems_file, 'w', encoding='utf-8')
        json.dump(data, write_file, indent=4, ensure_ascii=False)
        write_file.close()
        reply(message, "Создана новая система чатов с ID {}".format(new_id))
    else:
        reply(message, "Для этой операции прошу вызвать @DeMaximilianster")


def add_admin_place(message):
    """Add admin place to system"""
    log.log_print("add_admin_place invoked")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    if chat:
        system = chat["system"]
        database.change(message.chat.id, "admin_place", "systems", ('id', system))
        reply(message, "Теперь это чат админов. Я сюда буду присылать различные уведомления!")


def chat_options(message):
    """Optimize current chat"""
    log.log_print("chat_options invoked")
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


def database_changer():
    database = Database()
    members = database.get_all('members')
    for member in members:
        database.change(1, 'system', 'members', ('id', member['id']))


# TODO Команда /add_channel
# TODO Команда /del_chat
# TODO Команда /del_channel
