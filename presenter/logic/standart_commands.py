# -*- coding: utf-8 -*-
from view.output import reply, send_photo, send_sticker, send
from presenter.config.config_func import time_replace, language_analyzer, case_analyzer
from presenter.config.database_lib import Database
from presenter.config.config_var import bot_id, admin_place, original_to_english, english_to_original, months
from random import choice
from time import ctime, time
from presenter.config.log import Loger, log_to
from presenter.config.texts import minets

log = Loger(log_to)


def language_getter(message):
    """Gets the language of the chat"""
    log.log_print(f"{__name__} invoked")
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
    del database


def helper(message):
    """Предоставляет человеку список команд"""
    log.log_print(str(message.from_user.id)+": helper invoked")
    answer = '*Команды:*\n\n'
    answer += '/help - Присылает это сообщение\n'
    answer += "/id - Присылает различные ID'шники, зачастую бесполезные\n"
    answer += '/minet - Делает приятно\n'
    answer += '/drakken - Присылает арт с Доктором Драккеном\n'
    answer += '/meme - Присылает хороший мем\n'
    answer += '/me - Присылает вашу запись в базе данных\n\n'

    answer += '/admin - Только для главадмина и его заместителя. Даёт человеку админку\n'
    answer += '/unadmin - Только для главадмина и его заместителя. Забирает у человека админку\n'
    reply(message, answer, parse_mode='Markdown')


def show_id(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    log.log_print(str(message.from_user.id)+": show_id invoked")
    answer = 'Время отправки вашего сообщения: ` ' + ctime(message.date) + '`\n\n'
    answer += 'Переводя, выходит: ` ' + str(time_replace(message.date)) + '`\n\n'
    answer += 'Время отправки моего сообщения: ` ' + ctime(time()) + '`\n\n'
    answer += 'ID этого чата: `' + str(message.chat.id) + '`\n\n'
    answer += 'Ваш ID: `' + str(message.from_user.id) + '`\n\n'
    answer += 'Ваш language code:  `{}`\n\n'.format(message.from_user.language_code)
    answer += 'ID вашего сообщения: `' + str(message.message_id) + '`\n\n'
    reply_msg = message.reply_to_message
    if reply_msg:  # Сообщение является ответом
        answer += 'ID человека, на сообщение которого ответили: `' + str(reply_msg.from_user.id) + '`\n\n'
        answer += 'Его/её language code:  `{}`\n\n'.format(reply_msg.from_user.language_code)
        answer += 'ID сообщения, на которое ответили: `' + str(reply_msg.message_id) + '`\n\n'
        if reply_msg.forward_from:  # Сообщение, на которое ответили, является форвардом
            answer += 'ID человека, написавшего пересланное сообщение: `' + str(reply_msg.forward_from.id) + '`\n\n'
            answer += 'Его/её language code:  `{}`\n\n'.format(reply_msg.forward_from.language_code)
        elif reply_msg.forward_from_chat:  # Сообщение, на которое ответили, является форвардом из канала
            answer += 'ID канала, из которого переслали сообщение: `' + str(reply_msg.forward_from_chat.id) + '`\n\n'
        if reply_msg.sticker:
            answer += 'ID стикера: `' + reply_msg.sticker.file_id + '`\n\n'
            # answer += 'Ссылка на набор с этим стикером: https://telegram.me/addstickers/'
            # answer += reply_msg.sticker.set_name + '\n\n'
        elif reply_msg.photo:
            answer += 'ID фотографии `' + reply_msg.photo[0].file_id + '`'
            for i in reply_msg.photo[1:]:
                answer += ',\n' + '`' + i.file_id + '`'
            answer += '\n\n'
        for media in (reply_msg.video, reply_msg.voice, reply_msg.video_note, reply_msg.audio, reply_msg.document):
            if media:
                answer += 'ID медиа: `' + media.file_id + '`\n\n'
                break
    reply(message, answer, parse_mode='Markdown')


def minet(message):
    """Приносит удовольствие"""
    log.log_print(str(message.from_user.id)+": minet invoked")
    language = language_analyzer(message, only_one=True)
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


def send_drakken(message):
    """Присылает арт с Доктором Драккеном"""
    log.log_print(str(message.from_user.id)+": send_drakken invoked")
    drakken = choice(('AgADAgADpqsxG3J5-Urrn-mZkdvjs1SnhQ8ABAEAAwIAA20AA9QNBAABFgQ',
                      'AgADAgADtaoxG3L2eUns8mJ7X9gm893qtw8ABAEAAwIAA20AA-gnAQABFgQ',
                      'AgADAgAD8asxG4SzgUm_RXHcgE4jd26xUQ8ABAEAAwIAA20AAzHIBQABFgQ',
                      'AgADAgAD06wxG6uiUEkjcLfrDsigh339tw8ABAEAAwIAA20AA8f_AAIWBA',
                      'AgADAgAD36oxG0ImAUvzgBI4oR5C9J_RuQ8ABAEAAwIAA20AA9FGAQABFgQ',
                      'AgADAgADRKoxG1QCQUmlG28vrK8o_avCtw8ABAEAAwIAA20AA8v1AAIWBA'))
    send_photo(message.chat.id, drakken, reply_to_message_id=message.message_id)
    # TODO Функция добавления большего количества Докторов Драккенов


def send_meme(message):
    """Присылает мем"""
    log.log_print(str(message.from_user.id)+": send_meme invoked")
    meme = choice(('AgADAgADx60xG2S_oUmVz41Dk8a4AkRNUw8ABAEAAwIAA20AAzj4BQABFgQ',
                   'AgADAgADdKsxG7PUsEmfWmu7wYQaSlHNuQ8ABAEAAwIAA20AA2gAAxYE',
                   'AgADAgAD-aoxG0EnIUqnHKx1l-EFFajiug8ABAEAAwIAA20AA3VUAAIWBA',
                   'AgADAgADY6sxG2RPyUmfTbFEJLvRV9Lhtw8ABAEAAwIAA20AA-lxAQABFgQ',
                   'AgADAgAD36sxG3h0uUlOXJnN-wooZiGxhQ8ABAEAAwIAA3gAA7nOAgABFgQ',
                   'AgADAgADJKsxG-KVuElBSmME_b_Cn8KghQ8ABAEAAwIAA20AA2DOAgABFgQ'))
    send_photo(message.chat.id, meme, reply_to_message_id=message.message_id)


def send_me(message, person):
    """Присылает человеку его запись в БД"""
    log.log_print(str(message.from_user.id)+": send_me invoked")
    database = Database()
    chats_ids = [x[0] for x in database.get_many('chats', ('messages_count', 2))]
    msg_count = 0
    for chat_id in chats_ids:
        if database.get('messages', ('person_id', person.id), ('chat_id', chat_id)):
            msg_count += database.get('messages', ('person_id', person.id), ('chat_id', chat_id))[2]
    database.change(person.username, 'username', 'members', ('id', person.id))
    database.change(person.first_name, 'nickname', 'members', ('id', person.id))
    database.change(msg_count, 'messages', 'members', ('id', person.id))
    # TODO Вынести всё это дело в функцию member_update()
    p = database.get('members', ('id', person.id))
    print(p)
    appointments = [x[1] for x in database.get_many('appointments', ('id', person.id))]
    if database.get('messages', ('person_id', person.id), ('chat_id', message.chat.id)):
        messages_here = database.get('messages', ('person_id', person.id), ('chat_id', message.chat.id))[2]
    else:
        messages_here = 0
    msg = 'ID: {}\n'.format(p[0])
    msg += 'Юзернейм: {}\n'.format(p[1])
    msg += 'Никнейм: {}\n'.format(p[2])
    msg += 'Ранг: {}\n'.format(p[3])
    msg += 'Кол-во сообщений в этом чате: {}\n'.format(messages_here)
    msg += 'Кол-во сообщений во всём МФ2: {}\n'.format(p[4])
    msg += 'Кол-во предупреждений: {}\n'.format(p[5])
    msg += 'Кол-во ябломилианов: {}\n'.format(p[6])
    msg += 'Должности: ' + ', '.join(appointments)
    reply(message, msg)
    del database


def all_members(message):
    """Присылает человеку все записи в БД"""
    log.log_print("all_members invoked")
    database = Database()
    members = database.get_all('members', 'messages')
    sent = None
    if len(members) % 50 == 0:
        fiftys = len(members) // 50
    else:
        fiftys = len(members) // 50 + 1
    for fifty in range(fiftys):
        one_message_list = members[50*(fifty-1): 50*fifty]
        answer = ''
        for member in one_message_list:
            username = "[{}](tg://user?id={})".format(member[2].replace('[', '').replace(']', ''), member[0])
            answer += '`' + str(member[0]) + '` ' + username + '\n'
        sent = send(message.from_user.id, answer, parse_mode='Markdown')
    if sent:
        reply(message, "Выслал БД в личку")
    else:
        reply(message, "Сначала запусти меня в личных сообщениях")


def money_give(message, person):
    """Функция обмена деньгами между людьми"""
    log.log_print(f"money_give invoked to person {person.id}")
    database = Database()
    getter = person.id
    giver = message.from_user.id
    money = message.text.split()[-1]
    value_getter = database.get('members', ('id', getter))[6]
    value_giver = database.get('members', ('id', giver))[6]
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
            giv_m = send(giver, f"#Финансы\n\n Вы успешно перевели {money} ЯМ на счёт {getter}. "
                                f"Теперь у вас их {value_giver}. А у него/неё {value_getter}")
            get_m = send(getter, f"#Финансы\n\n На ваш счёт было {money} ЯМ со счёта {giver}. "
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
                           f"ID {getter} [{value_getter-money} --> {value_getter}] {get_m}\n"
                           f"ID {giver} [{value_giver+money} --> {value_giver}] {giv_m}\n")
            send(admin_place(database), f"#Финансы #Ф{getter} #Ф{giver}\n\n"
                                        f"ID {getter} [{value_getter-money} --> {value_getter}] {get_m}\n"
                                        f"ID {giver} [{value_giver+money} --> {value_giver}] {giv_m}\n")
    database.change(value_getter, 'money', 'members', ('id', getter))
    database.change(value_giver, 'money', 'members', ('id', giver))
    del database


def money_top(message):
    log.log_print(f"{__name__} invoked")
    database = Database()
    bot_money = database.get('members', ('id', bot_id))[6]
    people = list(database.get_all("members", 'money'))
    people = filter(lambda x: x[6] != 0 and x[0] != bot_id, people)
    i = 1
    text = "Бюджет: {} 🍎\n".format(bot_money)
    for person in people:
        text += "\n{}. {} -- {} 🍎".format(i, person[2], person[6])  # TODO Добавить сюда красивые ссылки на чела
        i += 1
    reply(message, text)
    del database


# TODO More comfortable way to insert birthday
def month_set(message, month):
    log.log_print(f"{__name__} invoked")
    database = Database()
    reply(message, "Ставлю человеку с ID {} месяц рождения {}".format(message.from_user.id, month))
    database.change(month, 'month_birthday', 'members', ('id', message.from_user.id))
    del database


def day_set(message, day):
    log.log_print(f"{__name__} invoked")
    days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    database = Database()
    month = database.get('members', ('id', message.from_user.id))[7]
    lang = language_analyzer(message, only_one=True)
    if not month:
        reply(message, "Сначала поставь месяц рождения")
    elif day > days[month - 1]:
        month = months[month][lang]
        month = case_analyzer(month, 'Russian')
        reply(message, "В {} нет столько дней".format(month.lower()))
    else:
        reply(message, "Ставлю человеку с ID {} день рождения {}".format(message.from_user.id, day))
        database.change(day, 'day_birthday', 'members', ('id', message.from_user.id))
    del database


def birthday(message):
    log.log_print(f"{__name__} invoked")
    database = Database()
    people = list(database.get_all("members", "month_birthday", how_sort='ASC'))
    # TODO Better sorting algorithm
    people = filter(lambda x: x[7] and x[8], people)
    lang = language_analyzer(message, only_one=True)
    i = 1
    text = ""
    for person in people:
        text += "\n{}. {} -- {} {} ".format(i, person[2], months[person[7]][lang], person[8])
        # TODO Добавить сюда красивые ссылки на чела
        i += 1
    reply(message, text)
    del database

def admins(message):
    database = Database()
    admins_id = [admin[0] for admin in database.get_many('appointments', ('appointment', 'Admin'))]
    admins_username = ['@'+database.get('members', ('id', admin))[1] for admin in admins_id]
    reply(message, 'Вызываю сюда админов:\n ' + ' '.join(admins_username))
