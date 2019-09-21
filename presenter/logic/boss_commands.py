# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from presenter.config.config_var import full_chat_list, chat_list, channel_list
import presenter.config.log as log
from view.output import kick, reply, promote, send, forward
work = True
log = log.Loger(log.LOG_TO_CONSOLE)  # TODO доделать этот прикол здесь и в остальных logic модулях

# TODO команда /warn
# TODO команда /unwarn
# TODO команда /unban
# TODO команда для делания гражданином, высшим гражданином
# TODO команда для делания Членом Комитета


def warn(message):
    """Даёт участнику предупреждение"""
    database = Database()
    person = message.reply_to_message.from_user
    value = database.get(person.id)[5] + 1
    database.change(value, person.id, table='members', set_column='warns', where_column='id')
    reply(message, "Варн выдан. Теперь их {}".format(value))
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


def ban(message):
    """Даёт участнику бан"""
    send(message.chat.id, "Ну всё, этому челику жопа")
    database = Database()
    database.change("Нарушитель", message.reply_to_message.from_user.id, 'members', 'rank', 'id')
    del database
    for chat in full_chat_list:
        kick(chat[0], message.reply_to_message.from_user.id)
    for channel in channel_list:
        kick(channel[0], message.reply_to_message.from_user.id)


def deleter_mode(message):
    """Удалять медиа или нет"""
    global delete
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


def promotion(message):
    """Назначает человека админом"""
    database = Database()
    database.change("Админ", message.reply_to_message.from_user.id, 'members', 'rank', 'id')
    # TODO пусть бот шлёт админу ссылку на чат админосостава и меняет её при входе
    # TODO давать админку, не пингуя
    # TODO сделать сменяемого зама автоматически (команда /vice)
    chats_promoted = []  # Сюда запишем все чаты, где чел словил админку
    channels_promoted = []  # А сюда все каналы
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list:
        promote(chat[0], message.reply_to_message.from_user.id,
                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
        chats_promoted.append(chat[1])
    for channel in channel_list:
        promote(channel[0], message.reply_to_message.from_user.id, can_post_messages=True, can_invite_users=True)
        channels_promoted.append(channel[1])
    text = "Господин, теперь этот человек является админом в чатах: " + ", ".join(chats_promoted) + "\n\n"
    text += "А так же в каналах: " + ", ".join(channels_promoted)
    reply(message, text)
    del database


def demotion(message):
    """Забирает у человека админку"""
    database = Database()
    database.change("Гость", message.reply_to_message.from_user.id, 'members', 'rank', 'id')
    # TODO забирать админку, не пингуя
    chats_promoted = []  # Сюда запишем все чаты, где чел потерял админку
    channels_promoted = []  # А сюда все каналы
    # Забрать у чела админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list:
        promote(chat[0], message.reply_to_message.from_user.id,
                can_change_info=False, can_delete_messages=False, can_invite_users=False,
                can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
        chats_promoted.append(chat[1])
    for channel in channel_list:
        promote(channel[0], message.reply_to_message.from_user.id, can_post_messages=False, can_invite_users=False)
        channels_promoted.append(channel[1])
    text = "Господин, теперь этот человек является гостем в чатах: " + ", ".join(chats_promoted) + "\n\n"
    text += "А так же в каналах: " + ", ".join(channels_promoted)
    reply(message, text)


def add_chat(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    database = Database()
    chat = (message.chat.id, message.chat.title, message.text[10:])
    database.append(chat, "chats")
    reply(message, "Теперь это часть МФ2. Учтите, что для корректного бана и админок, необходимо перезагрузить меня")
    del database
