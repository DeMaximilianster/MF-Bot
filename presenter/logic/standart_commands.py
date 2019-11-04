# -*- coding: utf-8 -*-
from view.output import reply, send_photo, send_sticker, send
from presenter.config.config_func import time_replace, person_analyze
from presenter.config.database_lib import Database
from random import choice
from time import ctime, time
from presenter.config.log import Loger, log_to

log = Loger(log_to)


def helper(message):
    """Предоставляет человеку список команд"""
    log.log_print(str(message.from_user.id)+": helper invoked")
    answer = '**Команды:**\n\n'
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
    answer += 'ID вашего сообщения: `' + str(message.message_id) + '`\n\n'
    reply_msg = message.reply_to_message
    if reply_msg:  # Сообщение является ответом
        answer += 'ID человека, на сообщение которого ответили: `' + str(reply_msg.from_user.id) + '`\n\n'
        answer += 'ID сообщения, на которое ответили: `' + str(reply_msg.message_id) + '`\n\n'
        if reply_msg.forward_from:  # Сообщение, на которое ответили, является форвардом
            answer += 'ID человека, написавшего пересланное сообщение: `' + str(reply_msg.forward_from.id) + '`\n\n'
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
    way = choice(('text', 'sticker'))
    if way == 'text':
        rep = choice(('оаоаоаоаооа мммммм)))))', 'Э, нет, эта кнопка не для тебя', 'Попа чистая?', 'Кусь :3',
                      'Открывай рот тогда)', 'О, да, эта кнопка для тебя', '😏🤤', 'Одна фелляция\nНикакой фрустрации'))
        reply(message, rep)
    else:
        rep = choice(('CAADAgADWAADBoAqF4oogkZzHIvuFgQ',  # УНО-карточка
                      'CAADBAADqlUAAuOnXQVKqOJLAf4RYBYE',  # ОК
                      'CAADAgADewAD6J0qFmJL_8KisLg8FgQ',  # Гамлет
                      'CAADAgADfAADq1fEC779DZWncMB2FgQ',  # Хонка
                      'CAADAgADLQADb925FmFcbIKhK_3CFgQ',  # Что-то нет настроения
                      'CAADAgADOAADb925FlKHKgxtlre-FgQ',  # Я с йогуртом
                      'CAADAgADGAADobczCKi7TanwsWyoFgQ',  # хоошо
                      'CAADAgADTwEAAqfkvganUQktSzVbkRYE'  # Инангай
                      ))
        send_sticker(message.chat.id, rep, reply_to_message_id=message.message_id)


def uberminet(message):
    """ПРИНОСИТ УДОВОЛЬСТВИЕ"""
    log.log_print(str(message.from_user.id)+": uberminet invoked")
    rep = choice(('оаоаоаоаооа мммммм)))))', 'Э, нет, эта кнопка не для тебя', 'Попа чистая?', 'Кусь :3',
                  'Открывай рот тогда)'))
    reply(message, " *"+rep.upper()+"!!!!!*", parse_mode='Markdown')


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


def send_me(message):
    """Присылает человеку его запись в БД"""
    log.log_print(str(message.from_user.id)+": send_me invoked")
    database = Database()
    person = person_analyze(message, True)
    if person:  # TODO Перенести проверку на person_analyze в input.py
        database.change(person.username, person.id, set_column='username')
        database.change(person.first_name, person.id, set_column='nickname')
        person = database.get(person.id)
        if person:
            msg = 'ID: {}\n'.format(person[0])
            msg += 'Юзернейм: {}\n'.format(person[1])
            msg += 'Никнейм: {}\n'.format(person[2])
            msg += 'Ранг: {}\n'.format(person[3])
            msg += 'Кол-во сообщений: {}\n'.format(person[4])
            msg += 'Кол-во предупреждений: {}\n'.format(person[5])
            msg += 'Количество ябломилианов: {}\n'.format(person[6])
        else:
            msg = "Не знаю, чё это такое тут сидит"
        reply(message, msg)
    del database


def all_members(message):
    """Присылает человеку все записи в БД"""
    log.log_print("all_members invoked")
    database = Database()
    members = database.get_all('members', 'messages')
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
        send(message.from_user.id, answer, parse_mode='Markdown')
    reply(message, "Выслал БД в личку")


def money_give(message):
    """Функция обмена деньгами между людьми"""
    database = Database()
    getter = person_analyze(message).id
    giver = message.from_user.id
    money = message.text.split()[-1]
    value_getter = database.get(getter)[6]
    value_giver = database.get(giver)[6]
    if not money.isdigit() and not (money[1:].isdigit() and money[0] == '-'):
        reply(message, "Последнее слово должно быть числом, сколько ябломилианов даёте")
    elif money[0] == '-':
        reply(message, "Неплохая попытка")
    else:
        money = int(money)
        if money > value_giver:
            reply(message, "Деньжат не хватает")
        else:
            value_getter += money
            value_giver -= money
            reply(message, "#Финансы\n\nID {} [{} --> {}]\nID {} [{} --> {}]\n"
                  .format(getter, value_getter-money, value_getter, giver, value_giver+money, value_giver))
            admin_place = database.get("Админосостав", 'chats', 'purpose')[0]
            send(admin_place, "#Финансы\n\nID {} [{} --> {}]\nID {} [{} --> {}]\n"
                 .format(getter, value_getter-money, value_getter, giver, value_giver+money, value_giver))
    database.change(value_getter, getter, 'members', 'money', 'id')
    database.change(value_giver, giver, 'members', 'money', 'id')
    del database
