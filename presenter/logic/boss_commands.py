# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from presenter.config.config_var import full_chat_list, chat_list, channel_list, bot_id, admin_place
from presenter.config.log import Loger, log_to
from view.output import kick, reply, promote, send, forward
work = True
log = Loger(log_to)

# TODO функция unwarn
# TODO команда /kick, кикает и сразу разбанивает

# TODO команда для делания гражданином, высшим гражданином
# TODO команда для делания Членом Комитета
# TODO сделать сменяемого зама автоматически (команда /vice)

"""
def chat_search(message):
    reply(message, "Приступаю к выполнению")
    # i = -1001250000000
    i = "@trachDeMax"
    while True:
        chat = get_chat(i)
        if chat:
            if chat.username:
                send(message.chat.id, chat.username)
                break
            else:
                send(message.chat.id, "Нашёл супергруппу, но она приватная")
        elif i % 100 == 0:
            send(message.chat.id, "Достиг отметки в {}".format(i))
        i -= 1
"""


def warn(message, person):
    """Даёт участнику предупреждение"""
    log.log_print("warn invoked")
    database = Database()
    try:  # TODO поменять на if-else
        warns = int(message.text.split()[1])
    except Exception as e:
        print(e)
        warns = 1
    value = database.get('members', ('id', person.id))[5] + warns
    database.change(value, person.id, table='members', set_column='warns', where_column='id')
    reply(message, "Варн(ы) выдан(ы). Теперь их {}".format(value))
    blowout = database.get('channels', ('name', 'Проколы'))[0]
    how_many = 20  # Сколько пересылает сообщений
    end_forwarding = message.reply_to_message.message_id
    start_forwarding = end_forwarding - how_many
    send(blowout, "В чате '{}' случилось нарушение участником {} (@{}) [{}]. Прысылаю {} сообщений".
         format(message.chat.title, person.first_name, person.username, person.id, how_many))
    for msg_id in range(start_forwarding, end_forwarding+1):
        forward(blowout, message.chat.id, msg_id)
    if value >= 3:
        ban(message, person)
    del database


def unwarn(message, person):
    """Снимает с участника предупреждение"""
    log.log_print("unwarn invoked")
    database = Database()
    value = database.get('members', ('id', person.id))[5] - 1  # TODO Возможность снимать несколько варнов за раз
    # TODO Предохранитель от отрицательного числа варнов
    database.change(value, person.id, table='members', set_column='warns', where_column='id')
    reply(message, "Варн снят. Теперь их {}".format(value))
    if value < 3:
        pass  # TODO команда /unban
    del database


# TODO команда /kick, которая даёт бан и сразу его снимает
def ban(message, person):
    """Даёт участнику бан"""
    log.log_print("ban invoked")
    database = Database()
    blowout = database.get('channels', ('name', 'Проколы'))[0]
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


def money_pay(message, person):
    """Платит человеку деньги из бюджета чата"""
    log.log_print(f"money pay invoked to person {person.id}")
    database = Database()
    bot_money = database.get('members', ('id', bot_id))[6]
    p_id = person.id
    money = message.text.split()[-1]
    value = database.get('members', ('id', p_id))[6]
    if not money.isdigit() and not (money[1:].isdigit() and money[0] == '-'):
        reply(message, "Последнее слово должно быть числом, сколько ябломилианов прибавляем или убавляем")
    elif money == "0":
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
    elif money[0] == '-':
        money = -int(money)  # Делаем из отрицательного числа положительное
        if value-money >= 0:
            value -= money
            bot_money += money
            sent = send(p_id, f"#Финансы\n\n"
                              f"С вашего счёта было снято {money} ЯМ в фонд чата. У вас осталось {value} ЯМ")
            if sent:
                sent = "✅ уведомлён(а)"
            else:
                sent = "❌ не уведомлён(а)"
            reply(message, f"#Финансы #Бюджет #Ф{p_id}\n\n"
                           f"Бюджет [{bot_money-money} --> {bot_money}]\n"
                           f"ID {p_id} [{value+money} --> {value}] {sent}")
            send(admin_place, f"#Финансы #Бюджет #Ф{p_id}\n\n"
                              f"Бюджет [{bot_money-money} --> {bot_money}]\n"
                              f"ID {p_id} [{value+money} --> {value}] {sent}")
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
                sent = "✅ уведомлён(а)"
            else:
                sent = "❌ не уведомлён(а)"
            reply(message, f"#Финансы #Бюджет #Ф{p_id}\n\n"
                           f"Бюджет [{bot_money+money} --> {bot_money}]\n"
                           f"ID {p_id} [{value-money} --> {value}] {sent}")

            send(admin_place, f"#Финансы #Бюджет #Ф{p_id}\n\n"
                              f"Бюджет [{bot_money+money} --> {bot_money}]\n"
                              f"ID {p_id} [{value-money} --> {value}] {sent}")
    database.change(value, p_id, 'members', 'money', 'id')
    database.change(bot_money, bot_id, 'members', 'money', 'id')
    del database


def promotion(message, person):
    """Назначает человека админом"""
    log.log_print("promotion invoked")
    database = Database()
    database.change("Админ", person.id, 'members', 'rank', 'id')
    # TODO пусть бот шлёт админу ссылку на чат админосостава и меняет её при входе
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list:
        promote(chat[0], person.id,
                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
    for channel in channel_list:
        promote(channel[0], person.id, can_post_messages=True, can_invite_users=True)
    reply(message, "Теперь это админ!")
    del database


def demotion(message, person):
    """Забирает у человека админку"""
    log.log_print("demotion invoked")
    database = Database()
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


def message_change(message, person):
    """Меняет запись в БД о количестве сообщений чела"""
    log.log_print(f"message_change invoked to person {person.id}")
    database = Database()
    p_id = person.id
    messages = message.text.split()[-1]
    value = database.get('members', ('id', p_id))[4]
    if not messages.isdigit() and not (messages[1:].isdigit() and messages[0] == '-'):
        reply(message, "Последнее слово должно быть числом, сколько сообщений ставим, прибавляем или убавляем")
    elif messages[0] == '+':
        messages = int(messages)
        value += messages
        reply(message, "Прибавляю человеку с ID {} {} сообщений. В итоге получается {}".format(p_id, messages, value))
    elif messages[0] == '-':
        messages = -int(messages)  # Делаем из отрицательного числа положительное
        value -= messages
        if value >= 0:
            reply(message, "Отнимаю человеку с ID {} {} сообщений. В итоге получается {}".format(p_id, messages, value))
        else:
            reply(message, "Часто у людей видишь отрицательное количество сообщений?")

    else:
        value = int(messages)
        reply(message, "Ставлю человеку с ID {} количество сообщений равное {}".format(p_id, value))
    database.change(value, p_id, 'members', 'messages', 'id')
    del database


def deleter_mode(message):
    """Удалять медиа или нет"""
    log.log_print("deleter_mode invoked")
    database = Database()
    delete = int(database.get('config', ('var', 'delete'))[1])
    delete = (delete + 1) % 2  # Переводит 0 в 1, а 1 в 0
    database.change(delete, 'delete', 'config', 'value', 'var')
    del database
    if delete:
        reply(message, 'Окей, господин, теперь я буду удалять медиа, которые присланы гостями')
    else:
        reply(message, 'Окей, гости могут спокойной слать свои медиа')


def add_chat(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    # TODO Предохранитель на purpose чата
    # TODO Предохранитель на уникальность некоторых чатов
    log.log_print("add_chat invoked")
    database = Database()
    chat = (message.chat.id, message.chat.title, message.text[10:])
    database.append(chat, "chats")
    # TODO Пофиксить необходимость перезагрузки
    reply(message, "Теперь это часть МФ2. Учтите, что для корректного бана и админок, необходимо перезагрузить меня")
    del database


# TODO Команда /add_channel
# TODO Команда /del_chat
# TODO Команда /del_channel
