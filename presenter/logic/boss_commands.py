# -*- coding: utf-8 -*-
from presenter.config.config_func import Database
from presenter.config.config_var import full_chat_list, chat_list
import presenter.config.log as log
from view.output import kick, reply, promote
work = True
log = log.Loger(log.LOG_TO_CONSOLE)  # TODO доделать этот прикол здесь и в остальных logic модулях

# TODO команда /warn
# TODO команда /unwarn
# TODO команда /unban
# TODO команда для делания гражданином, высшим гражданином
# TODO команда для делания Членом Комитета

'''
@bot.message_handler(commands=['warn'])
def warn(message):
    """Даёт участнику предупреждение"""
    if not in_mf(message, False):
        return None
    database = Database()
    rank = database.get(message.from_user.id)[3]  # Получаем его звание
    if rank != "Админ" and rank != "Член Комитета" and rank != "Заместитель" and rank != "Лидер":
        bot.reply_to(message, "Э, нет, эта кнопка только для админов")
        return None
    database = Database()
    person = database.get(message.from_user.id)
    value = database.get(person.id)[5] + 1  # TODO автопостинг пруфов
    del database
'''


def ban(message):
    """Даёт участнику бан"""

    database = Database()
    database.change("Нарушитель", message.reply_to_message.from_user.id, 'members', 'rank', 'id')
    del database
    for chat in full_chat_list:
        kick(chat[0], message.reply_to_message.from_user.id)


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
    # TODO надо его ещё научить быть на канале недостримов и голосовашек и там тоже порядки наводить
    # TODO сделать сменяемого зама автоматически (команда /vice)
    chats_promoted = []  # Сюда запишем все чаты, где чел словил админку
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list:
        promote(chat[0], message.reply_to_message.from_user.id,
                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
        chats_promoted.append(chat[1])
    reply(message, "Господин, теперь этот человек является админом в чатах: " + ", ".join(chats_promoted))
    del database


def demotion(message):
    """Забирает у человека админку"""
    database = Database()
    database.change("Гость", message.reply_to_message.from_user.id, 'members', 'rank', 'id')
    # TODO забирать админку, не пингуя
    chats_promoted = []  # Сюда запишем все чаты, где чел словил админку
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list:
        promote(chat[0], message.reply_to_message.from_user.id,
                can_change_info=False, can_delete_messages=False, can_invite_users=False,
                can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
        chats_promoted.append(chat[1])
    reply(message, "Господин, теперь этот человек является гостем в чатах: " + ", ".join(chats_promoted))
    del database


def add_chat(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    database = Database()
    chat = (message.chat.id, message.chat.title, message.text[10:])
    database.append(chat, "chats")
    reply(message, "Теперь это часть МФ2. Учтите, что для корректного бана и админок, необходимо перезагрузить меня")
    del database
