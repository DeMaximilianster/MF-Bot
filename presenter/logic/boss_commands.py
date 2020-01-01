# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from presenter.config.config_var import full_chat_list, channel_list, bot_id, admin_place, chat_list
from presenter.config.log import Loger, log_to
from presenter.config.config_func import unban_user
from view.output import kick, reply, promote, send, forward

work = True
log = Loger(log_to)

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
    if len(message.text.split()) > 1:
        warns = int(message.text.split()[-1])  # TODO Эта проверка происходит дважды
    else:
        warns = 1
    if warns == 0:
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
        return None
    value = database.get('members', ('id', person.id))['warns'] + warns
    database.change(value, 'warns', 'members', ('id', person.id))
    reply(message, "Варн(ы) выдан(ы). Теперь их {}".format(value))
    blowout = database.get('channels', ('name', 'Проколы'))['id']
    how_many = 20  # Сколько пересылает сообщений
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
    if unwarns == 0:
        reply(message, "Я вам запрещаю делать подобные бессмысленные запросы")
        return None
    value = database.get('members', ('id', person.id))['warns'] - unwarns
    database.change(value, 'warns', 'members', ('id', person.id))
    reply(message, "Варн(ы) снят(ы). Теперь их {}".format(value))
    if value < 3:
        set_guest(message, person)


def ban(message, person):
    """Даёт участнику бан"""
    log.log_print("ban invoked")
    database = Database()
    blowout = database.get('channels', ('name', 'Проколы'))['id']
    how_many = 10  # Сколько пересылает сообщений
    target = message
    if message.reply_to_message:
        target = message.reply_to_message
    end_forwarding = target.message_id
    start_forwarding = end_forwarding - how_many
    send(blowout, "В чате '{}' забанили участника {} (@{}) [{}]. Прысылаю {} сообщений".
         format(message.chat.title, person.first_name, person.username, person.id, how_many))
    for msg_id in range(start_forwarding, end_forwarding + 1):
        forward(blowout, message.chat.id, msg_id)
    send(message.chat.id, "Ну всё, этому челику жопа")
    database.change('Violator', 'rank', 'members', ('id', person.id))
    for chat in full_chat_list(database):
        kick(chat['id'], person.id)
    for channel in channel_list(database):
        kick(channel['id'], person.id)


def money_pay(message, person):
    """Платит человеку деньги из бюджета чата"""
    # TODO Добавить уведомление о человеке, совершившем перевод
    # TODO add nice link's to people instead of id's
    log.log_print(f"money pay invoked to person {person.id}")
    database = Database()
    bot_money = database.get('members', ('id', bot_id))['money']
    p_id = person.id
    money = message.text.split()[-1]
    value = database.get('members', ('id', p_id))['money']
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
            send(admin_place(database), f"#Финансы #Бюджет #Ф{p_id}\n\n"
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

            send(admin_place(database), f"#Финансы #Бюджет #Ф{p_id}\n\n"
                                        f"Бюджет [{bot_money + money} --> {bot_money}]\n"
                                        f"ID {p_id} [{value - money} --> {value}] {sent}")
    database.change(value, 'money', 'members', ('id', p_id))
    database.change(bot_money, 'money', 'members', ('id', bot_id))


def give_admin(message, person):
    """Назначает человека админом"""
    log.log_print(f"{__name__} invoked")
    database = Database()
    # TODO При повторном использовании команды не должна появляться новая запись
    database.append((person.id, "Admin"), table='appointments')
    # TODO пусть бот шлёт админу ссылку на чат админосостава и меняет её при входе
    # Дать челу админку во всех чатах, кроме Комитета и Админосостава
    for chat in chat_list(database):
        promote(chat['id'], person.id,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
    for channel in channel_list(database):
        print(channel)
        promote(channel['id'], person.id, can_change_info=True, can_post_messages=True, can_invite_users=True)
    reply(message, "Теперь это админ!")


def del_admin(message, person):
    log.log_print(f"{__name__} invoked")
    database = Database()
    database.remove("appointments", ("appointment", "Admin"), ("id", person.id))
    for chat in chat_list(database):
        promote(chat['id'], person.id,
                can_change_info=False, can_delete_messages=False, can_invite_users=False,
                can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
    for channel in channel_list(database):
        promote(channel['id'], person.id, can_post_messages=False, can_invite_users=False)
    reply(message, "Теперь это не админ!")


def set_guest(message, person):
    """Sets person's rank to guest"""
    log.log_print(f"{__name__} invoked")
    database = Database()
    database.change("Guest", "rank", 'members', ('id', person.id))
    unban_user(person)
    del_admin(message, person)
    reply(message, "Теперь это гость!")


def set_citizen(message, person):
    """Sets person's rank to citizen"""
    log.log_print(f"{__name__} invoked")
    database = Database()
    database.change("Citizen", "rank", 'members', ('id', person.id))
    unban_user(person)
    del_admin(message, person)
    reply(message, "Теперь это гость!")


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
    # TODO Предохранитель на purpose чата
    # TODO Предохранитель на уникальность некоторых чатов
    log.log_print("add_chat invoked")
    database = Database()
    typee = 'private'
    link = 'None'
    if message.chat.username:
        typee = 'public'
        link = message.chat.username
    database.append((message.chat.id, message.chat.title, message.text[10:], typee, link, 2, 0, 0, 0, 0, 0, 0), 'chats')
    reply(message, "Теперь это часть МФ2. Как и:\n" + '\n'.join(map(str, full_chat_list(database))))


'''
def database_changer():
    database = Database()
    rank_shifter = {"Нарушитель": 'Violator',
                    "Гость": 'Guest',
                    "Гражданин": 'Citizen',
                    "Высший Гражданин": 'Senior Citizen',
                    "Член Комитета": 'The Committee Member',
                    "Заместитель": 'Deputy',
                    "Лидер": 'Leader'}
    members = database.get_all('members')
    for member in members:
        rank = member[3]
        if rank not in rank_shifter.values():
            rank = rank_shifter[rank]
            database.change(rank, 'rank', 'members', ('id', member[0]))
    
'''

# TODO Команда /add_channel
# TODO Команда /del_chat
# TODO Команда /del_channel
