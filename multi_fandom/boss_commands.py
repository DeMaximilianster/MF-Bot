# -*- coding: utf-8 -*-
from multi_fandom.config.config_var import *
boss_commands_work = True


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


@bot.message_handler(commands=['ban'])
def ban(message):
    """Даёт участнику бан"""
    if not in_mf(message, False):
        return None
    elif not is_admin(message):
        return None
    elif not message.reply_to_message:
        bot.reply_to(message, "Надо ответить на сообщение того, кого надо забанить")
        return None

    database = Database()
    database.change("Нарушитель", message.reply_to_message.from_user.id, 'members', 'rank', 'id')
    for chat in full_chat_list:
        try:
            bot.kick_chat_member(chat[0], message.reply_to_message.from_user.id)
        except Exception as e:
            print(e)
    del database


@bot.message_handler(commands=['delete_mode'])
def deleter_mode(message):
    """Удалять медиа или нет"""
    if not in_mf(message, False):
        return None
    elif not is_admin(message):
        return None
    global delete
    database = Database()
    delete = int(database.get('delete', 'config', 'var')[1])
    print(delete)
    delete = (delete + 1) % 2  # Переводит 0 в 1, а 1 в 0
    print(delete)
    database.change(delete, 'delete', 'config', 'value', 'var')
    del database
    if delete:
        bot.reply_to(message, 'Окей, господин, теперь я буду удалять медиа, которые присланы гостями')
    else:
        bot.reply_to(message, 'Окей, гости могут спокойной слать свои медиа')


@bot.message_handler(commands=['admin'])
def promotion(message):
    """Назначает человека админом"""
    if not in_mf(message, False):
        return None
    elif not is_admin(message, True):
        return None
    elif not message.reply_to_message:
        bot.reply_to(message, "Надо ответить на сообщение того, кого надо апгрейднуть")
        return None
    database = Database()
    database.change("Админ", message.reply_to_message.from_user.id, 'members', 'rank', 'id')

    # TODO пусть бот шлёт админу ссылку на чат админосостава и меняет её при входе
    # TODO давать админку, не пингуя
    # TODO надо его ещё научить быть на канале недостримов и голосовашек и там тоже порядки наводить
    # TODO сделать сменяемого зама автоматически (команда /vice)
    chats_promoted = []  # Сюда запишем все чаты, где чел словил админку
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list:
        try:
            bot.promote_chat_member(chat[0], message.reply_to_message.from_user.id,
                                    can_change_info=False, can_delete_messages=True, can_invite_users=True,
                                    can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
            chats_promoted.append(chat[1])
        except Exception as e:
            print(e)
    bot.reply_to(message, "Господин, теперь этот человек является админом в чатах: " + ", ".join(chats_promoted))
    del database


@bot.message_handler(commands=['guest'])
def firing(message):  # TODO пусть бот делает чела неадмином во всех чатах, где он есть
    """Забирает у человека админку"""  # TODO пусть бот ставит звание "гость"
    if not in_mf(message, False):
        return None
    elif not is_admin(message, True):
        return None
    elif not message.reply_to_message:
        bot.reply_to(message, "Надо ответить на сообщение того, кого надо даунгрейднуть")
        return None
    database = Database()
    database.change("Админ", message.reply_to_message.from_user.id, 'members', 'rank', 'id')
    # TODO забирать админку, не пингуя
    try:
        bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                can_change_info=False, can_delete_messages=False, can_invite_users=False,
                                can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
        bot.reply_to(message, "Господин, теперь этот человек является гостем")
    except Exception as e:
        error(message, e)
    del database


@bot.message_handler(commands=['add_chat'])
def add_chat(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    if not is_admin(message, True):
        return None
    database = Database()
    chat = (message.chat.id, message.chat.title, message.text[10:])
    database.append(chat, "chats")
    bot.reply_to(message, "Теперь это часть МФ2")
    del database
