# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from presenter.config.config_var import full_chat_list, channel_list, bot_id, admin_place, chat_list
from presenter.config.log import Loger, log_to
from presenter.config.config_func import unban_user, is_suitable, int_check, get_system_configs, photo_video_gif_get, \
    update_systems_json, create_system, create_chat, SystemUpdate, write_storage_json, get_storage_json,\
    person_info_in_html, chat_info_in_html
from view.output import kick, reply, promote, send, forward, restrict
from time import time

log = Loger(log_to)


def add_stuff_to_storage(message, stuff):
    log.log_print("add_stuff_to_storage")
    rep = message.reply_to_message
    data = get_storage_json()
    if rep:
        insert = photo_video_gif_get(rep)
        if insert:
            if list(insert) in data[stuff]:
                reply(message, "У меня это уже есть)")
            else:
                data[stuff].append(insert)
                forward(381279599, message.chat.id, rep.message_id)
                send(381279599, f"Норм контент?) user={message.from_user.id}, text={message.text}, id={insert[0]}")
                write_storage_json(data)
                reply(message, "ОК!")
        else:
            reply(message, "Ответить надо на гифку, фотографию или видео")
    else:
        reply(message, "Надо ответить на медиа, которое нужно добавить")


def update_all_members(message):
    log.log_print("money_top invoked")
    sent = reply(message, "Начинаю обновление...")
    database = Database(to_log=False)
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    members = list(database.get_many('members', ('system', system)))
    system_update = SystemUpdate(message.chat.id, system, members, sent)
    system_update.start()


def warn(message, person, parameters_dictionary):
    """Даёт участнику предупреждение"""
    log.log_print("warn invoked")
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
    # TODO каждому чату своё хранилище преступлений
    how_many = 10  # Сколько пересылает сообщений
    end_forwarding = message.reply_to_message.message_id
    start_forwarding = end_forwarding - how_many
    send(blowout, "В чате {} случилось нарушение участником {} Прысылаю {} сообщений".
         format(chat_info_in_html(message.chat), person_info_in_html(person), how_many), parse_mode='HTML')
    for msg_id in range(start_forwarding, end_forwarding + 1):
        forward(blowout, message.chat.id, msg_id)
    if value >= 3:  # TODO Выборочное количество варнов для бана для каждой системы
        ban(message, person)


def unwarn(message, person, parameters_dictionary: dict):
    """Снимает с участника предупреждение"""
    log.log_print("unwarn invoked")
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
            text += "Варн(ы) снят(ы) пользователем {}\n".format(person_info_in_html(message.from_user))
            if 'comment' in parameters_dictionary.keys():
                text += "Комментарий: {}".format(parameters_dictionary['comment'])
            send(adm_place, text, parse_mode='HTML')
        reply(message, "Варн(ы) снят(ы). Теперь их {}".format(value))
        if 3 - unwarns <= value < 3:
            chat_configs = get_system_configs(system)
            unban_user(person)
            database.change(chat_configs['ranks'][1], 'rank', 'members', ('id', person.id), ('system', system))
    else:
        reply(message, "Нельзя сделать отрицательное количество предупреждений")


def ban(message, person, comment=True, unban_then=False):
    """Даёт участнику бан"""
    log.log_print("ban invoked")
    database = Database()
    blowout = database.get('channels', ('name', 'Проколы'))['id']
    how_many = 3  # Сколько пересылает сообщений
    not_unban_then = not unban_then
    if not_unban_then:
        target = message
        if message.reply_to_message:
            target = message.reply_to_message
        end_forwarding = target.message_id
        start_forwarding = end_forwarding - how_many
        send(blowout, "В чате {} забанили участника {}. Прысылаю {} сообщений".
             format(chat_info_in_html(message.chat), person_info_in_html(person), how_many), parse_mode='HTML')
        for msg_id in range(start_forwarding, end_forwarding + 1):
            forward(blowout, message.chat.id, msg_id)
    if comment:
        send(message.chat.id, "Ну всё, этому челу " + "бан"*not_unban_then + "кик"*unban_then)
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    chat_configs = get_system_configs(system)
    if not unban_then:
        database.change(chat_configs['ranks'][0], 'rank', 'members', ('id', person.id), ('system', system))
    for chat in full_chat_list(database, system):
        kick(chat['id'], person.id)
    for channel in channel_list(database):
        kick(channel['id'], person.id)
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} получил(а) бан".format(
            person_info_in_html(person)+', но сразу и разбан'*unban_then), parse_mode='HTML')
    if unban_then:
        unban_user(person)


def mute(message, person, hours=1):
    """Даёт участнику бан"""
    log.log_print("mute invoked")
    database = Database()
    if len(message.text.split()) > 1:
        hours = int(message.text.split()[-1])
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    for chat in full_chat_list(database, system):
        restrict(chat['id'], person.id, until_date=time()+hours*3600)
    adm_place = admin_place(message, database)
    if adm_place:
        send(adm_place, "Пользователь {} получил(а) мут на {} час(ов)".format(person_info_in_html(person), hours),
             parse_mode='HTML')
    reply(message, "Мут выдан")


def money_pay(message, person, parameters_dictionary):
    """Платит человеку деньги из бюджета чата"""
    # TODO Добавить уведомление о человеке, совершившем перевод
    # TODO add nice link's to people instead of id's
    log.log_print(f"money pay invoked to person {person.id}")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    bot_money = database.get('systems', ('id', system))['money']
    not_inf = bot_money != 'inf'
    if not_inf:
        bot_money = int(bot_money)
    p_id = person.id
    money = parameters_dictionary['value']
    value = database.get('members', ('id', p_id), ('system', system))['money']
    if money == "0":
        reply(message, "Не")
    elif money[0] == '-':
        money = -int(money)  # Делаем из отрицательного числа положительное
        if value - money >= 0:
            value -= money
            if not_inf:
                bot_money += money
            sent = send(p_id, f"#Финансы\n\n"
                              f"С вашего счёта было снято {money} денег в фонд чата. У вас осталось {value} денег")
            # TODO Уточнять чат
            if sent:
                sent = "🔔 уведомлён(а)"
            else:
                sent = "🔕 не уведомлён(а)"
            answer = "#Финансы " + "#Бюджет "*not_inf + f"#f{p_id}\n\n"
            if not_inf:
                answer += f"Бюджет [{bot_money - money} --> {bot_money}]\n"
            answer += f"ID {p_id} [{value + money} --> {value}] {sent}"
            reply(message, answer)
            send(admin_place(message, database), answer)
        else:
            reply(message, "У людей число денег должно быть больше нуля")
    else:
        money = int(money)
        if not_inf and bot_money < money:
            reply(message, "У нас нет столько в бюджете")
        else:
            value += money
            if not_inf:
                bot_money -= money
            sent = send(p_id, f"#Финансы\n\n"
                              f"На ваш счёт было переведено {money} денег из фонда чата. Теперь у вас {value} денег")
            # TODO рефакторинг уведомлялки и переименование недег
            if sent:
                sent = "🔔 уведомлён(а)"
            else:
                sent = "🔕 не уведомлён(а)"
            answer = "#Финансы " + "#Бюджет " * not_inf + f"#f{p_id}\n\n"
            if not_inf:
                answer += f"Бюджет [{bot_money + money} --> {bot_money}]\n"
            answer += f"ID {p_id} [{value - money} --> {value}] {sent}"
            reply(message, answer)

            send(admin_place(message, database), answer)
    database.change(value, 'money', 'members', ('id', p_id), ('system', system))
    if not_inf:
        database.change(bot_money, 'money', 'systems', ('id', system))
    # TODO Засунуть эти зассанские уебанские денежные функции в отдельный блять модуль


def give_admin(message, person, loud=True):
    """Назначает человека админом"""
    log.log_print("give_admin invoked")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    # TODO пусть бот шлёт админу ссылку на чат админосостава и меняет её при входе
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list(database, system):
        promote(chat['id'], person.id,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
    for channel in channel_list(database):
        promote(channel['id'], person.id, can_post_messages=True, can_invite_users=True)
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
    # TODO Если у чела 3+ варна, то их нужно обнулить
    """Changes person's rank"""
    log.log_print("rank_changer invoked")
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
    log.log_print(f"message_change invoked to person {person.id}")
    database = Database()
    p_id = person.id
    ch_id = message.chat.id
    value = parameters_dictionary['value']
    reply(message, "Ставлю этому человеку в этот чат количество сообщений {}".format(value))
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
                    create_chat(message, system, typee, link, database)
                    reply(message, "Теперь я здесь работаю! Проверьте /help")
                else:
                    reply(message, "Произошла ошибка!")
            else:
                reply(message, "У вас в этой системе нет полномочий для добавления чатов в неё)")
        else:
            reply(message, "Такой системы не существует")
    elif message.from_user.id in [381279599]:  # Creating new system if adder is an MF diplomate
        all_systems = database.get_all('systems', 'id')
        ids = [int(sys['id']) for sys in all_systems]
        new_id = str(max(ids) + 1)
        create_chat(message, new_id, typee, link, database)
        create_system(message, new_id, database)
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
    else:
        reply(message, "Произошла ошибка!")


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


def system_options(message):
    """Optimize current system"""
    log.log_print("system_options invoked")
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


def money_mode_change(message):
    log.log_print("money_mode_change invoked")
    database = Database()

    mode = message.text.split()[0].split(sep='@')[0].split(sep='_')[-1]

    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    update_systems_json(system, mode == 'on', 'money')
    if mode == 'on':
        all_money = message.text.split()[-1]
        if int_check(all_money, positive=True):
            all_money = int(all_money)
            people = list(database.get_many('members', ('system', system)))
            people = list(filter(lambda x: x['money'] != 0 and x['id'] != bot_id, people))
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


def money_emoji(message):
    log.log_print("money_emoji invoked")
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


def money_name(message):
    # TODO Добавить проверку по падежам
    log.log_print("money_name invoked")
    database = Database()
    mode = ' '.join(message.text.split()[1:])
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    if mode:
        update_systems_json(system, mode, 'money_name')
        reply(message, "OK!")
    else:
        reply(message, "После команды введите название валюты")


def database_changer():
    database = Database()
    members = database.get_all('members')
    for member in members:
        database.change(1, 'system', 'members', ('id', member['id']))


# TODO Команда /add_channel
# TODO Команда /del_chat
# TODO Команда /del_channel
