# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from presenter.config.config_var import full_chat_list, chat_list, channel_list
from presenter.config.log import Loger, log_to
from presenter.config.config_func import person_analyze
from view.output import kick, reply, promote, send, forward
work = True
log = Loger(log_to)

# TODO команда /unwarn

# TODO команда для делания гражданином, высшим гражданином
# TODO команда для делания Членом Комитета


def warn(message):
    """Даёт участнику предупреждение"""
    log.log_print("warn invoked")
    database = Database()
    person = person_analyze(message)
    try:  # TODO поменять на if-else
        warns = int(message.text.split()[1])
    except Exception as e:
        print(e)
        warns = 1
    value = database.get(person.id)[5] + warns
    database.change(value, person.id, table='members', set_column='warns', where_column='id')
    reply(message, "Варн(ы) выдан(ы). Теперь их {}".format(value))
    blowout = database.get('Проколы', table='channels', column='name')[0]
    how_many = 20  # Сколько пересылает сообщений
    end_forwarding = message.reply_to_message.message_id
    start_forwarding = end_forwarding - how_many
    send(blowout, "В чате '{}' случилось нарушение участником {} (@{}) [{}]. Прысылаю {} сообщений".
         format(message.chat.title, person.first_name, person.username, person.id, how_many))
    for msg_id in range(start_forwarding, end_forwarding+1):
        forward(blowout, message.chat.id, msg_id)
    if value >= 3:
        ban(message)
    del database


def unwarn(message):
    """Снимает с участника предупреждение"""
    log.log_print("unwarn invoked")
    database = Database()
    person = person_analyze(message)
    value = database.get(person.id)[5] - 1  # TODO Возможность снимать несколько варнов за раз
    # TODO Предохранитель от отрицательного числа варнов
    database.change(value, person.id, table='members', set_column='warns', where_column='id')
    reply(message, "Варн снят. Теперь их {}".format(value))
    if value < 3:
        pass  # TODO команда /unban
    del database


# TODO команда /kick, которая даёт бан и сразу его снимает
def ban(message):
    """Даёт участнику бан"""
    log.log_print("ban invoked")
    database = Database()
    person = person_analyze(message)
    blowout = database.get('Проколы', table='channels', column='name')[0]
    how_many = 10  # Сколько пересылает сообщений
    end_forwarding = message.reply_to_message.message_id
    start_forwarding = end_forwarding - how_many
    send(blowout, "В чате '{}' забанили участника {} (@{}) [{}]. Прысылаю {} сообщений".
         format(message.chat.title, person.first_name, person.username, person.id, how_many))
    for msg_id in range(start_forwarding, end_forwarding + 1):
        forward(blowout, message.chat.id, msg_id)
    send(message.chat.id, "Ну всё, этому челику жопа")
    database.change("Нарушитель", person.id, 'members', 'rank', 'id')
    for chat in full_chat_list:
        kick(chat[0], person.id)
    for channel in channel_list:
        kick(channel[0], person.id)
    del database


def promotion(message):
    """Назначает человека админом"""
    log.log_print("promotion invoked")
    database = Database()
    person = person_analyze(message)
    database.change("Админ", person.id, 'members', 'rank', 'id')
    # TODO пусть бот шлёт админу ссылку на чат админосостава и меняет её при входе
    # TODO давать админку, не пингуя
    # TODO сделать сменяемого зама автоматически (команда /vice)
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list:
        promote(chat[0], person.id,
                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
    for channel in channel_list:
        promote(channel[0], person.id, can_post_messages=True, can_invite_users=True)
    reply(message, "Теперь это админ!")
    del database


def demotion(message):
    """Забирает у человека админку"""
    log.log_print("demotion invoked")
    database = Database()
    person = person_analyze(message)
    database.change("Гость", person.id, 'members', 'rank', 'id')
    # TODO забирать админку, не пингуя
    # Забрать у чела админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list:
        promote(chat[0], person.id,
                can_change_info=False, can_delete_messages=False, can_invite_users=False,
                can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
    for channel in channel_list:
        promote(channel[0], person.id, can_post_messages=False, can_invite_users=False)
    reply(message, "Теперь это гость!")
    del database


def message_change(message):
    """Меняет запись в БД о количестве сообщений чела"""
    database = Database()
    p_id = person_analyze(message).id
    messages = message.text.split()[-1]
    if messages[0] == '+':
        messages = int(messages)
        value = database.get(p_id)[4] + messages
        reply(message, "Прибавляю человеку с ID {} {} сообщений. В итоге получается {}".format(p_id, messages, value))
    elif messages[0] == '-':
        messages = -int(messages)  # Делаем из отрицательного числа положительное
        value = database.get(p_id)[4] - messages
        if value >= 0:
            reply(message, "Отнимаю человеку с ID {} {} сообщений. В итоге получается {}".format(p_id, messages, value))
        else:
            reply(message, "Часто у людей видишь отрицательное количество сообщений?")
            value = database.get(p_id)[4]
    else:
        value = int(messages)
        reply(message, "Ставлю человеку с ID {} количество сообщений равное {}".format(p_id, value))
    database.change(value, p_id, 'members', 'messages', 'id')
    del database


def deleter_mode(message):
    """Удалять медиа или нет"""
    log.log_print("deleter_mode invoked")
    database = Database()
    delete = int(database.get('delete', 'config', 'var')[1])
    print(delete)
    delete = (delete + 1) % 2  # Переводит 0 в 1, а 1 в 0
    print(delete)
    database.change(delete, 'delete', 'config', 'value', 'var')
    del database
    if delete:
        reply(message, 'Окей, господин, теперь я буду удалять медиа, которые присланы гостями')
    else:
        reply(message, 'Окей, гости могут спокойной слать свои медиа')


def add_chat(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    log.log_print("add_chat invoked")
    database = Database()
    chat = (message.chat.id, message.chat.title, message.text[10:])
    database.append(chat, "chats")
    reply(message, "Теперь это часть МФ2. Учтите, что для корректного бана и админок, необходимо перезагрузить меня")
    del database
