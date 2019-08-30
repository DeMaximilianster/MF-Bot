# -*- coding: utf-8 -*-
from multi_fandom.config.config_var import *
from random import choice
from time import ctime, time
import log as l
standart_commands_work = True

log = l.Loger(l.LOG_TO_CONSOLE)
@bot.message_handler(commands=['help'])
def helper(message):
    """Предоставляет человеку список команд"""
    if not in_mf(message):
        return None
    log.logPrint(str(message.from_user.id)+": helper invoked")
    answer = '**Команды:**\n\n'
    answer += '/help - Присылает это сообщение\n'
    answer += "/id - Присылает различные ID'шники, зачастую бесполезные\n"
    answer += '/minet - Делает приятно\n'
    answer += '/drakken - Присылает арт с Доктором Драккеном\n'
    answer += '/meme - Присылает хороший мем\n'
    answer += '/me - Присылает вашу запись в базе данных\n\n'

    answer += '/admin - Только для главадмина и его заместителя. Даёт человеку админку\n'
    answer += '/unadmin - Только для главадмина и его заместителя. Забирает у человека админку\n'
    bot.reply_to(message, answer, parse_mode='Markdown')


@bot.message_handler(commands=['id'])
def show_id(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    if not in_mf(message):
        return None
    log.logPrint(str(message.from_user.id)+": show_id invoked")
    answer = 'Время отправки вашего сообщения: ` ' + ctime(message.date) + '`\n\n'
    answer += 'Переводя, выходит: ` ' + str(time_replace(message.date)) + '`\n\n'
    answer += 'Время отправки моего сообщения: ` ' + ctime(time()) + '`\n\n'
    answer += 'ID этого чата: `' + str(message.chat.id) + '`\n\n'
    answer += 'Ваш ID: `' + str(message.from_user.id) + '`\n\n'
    answer += 'ID вашего сообщения: `' + str(message.message_id) + '`\n\n'
    reply = message.reply_to_message
    if reply:  # Сообщение является ответом
        answer += 'ID человека, на сообщение которого ответили: `' + str(reply.from_user.id) + '`\n\n'
        answer += 'ID сообщения, на которое ответили: `' + str(reply.message_id) + '`\n\n'
        if reply.forward_from:  # Сообщение, на которое ответили, является форвардом
            answer += 'ID человека, написавшего пересланное сообщение: `' + str(reply.forward_from.id) + '`\n\n'
        elif reply.forward_from_chat:  # Сообщение, на которое ответили, является форвардом из канала
            answer += 'ID канала, из которого переслали сообщение: `' + str(reply.forward_from_chat.id) + '`\n\n'
        if reply.sticker:
            answer += 'ID стикера: `' + reply.sticker.file_id + '`\n\n'
            answer += 'Ссылка на набор с этим стикером: https://telegram.me/addstickers/'
            answer += reply.sticker.set_name + '\n\n'
        elif reply.photo:
            answer += 'ID фотографии `' + reply.photo[0].file_id + '`'
            for i in reply.photo[1:]:
                answer += ',\n' + '`' + i.file_id + '`'
            answer += '\n\n'
        for media in (reply.video, reply.voice, reply.video_note, reply.audio, reply.document):
            if media:
                answer += 'ID медиа: `' + media.file_id + '`\n\n'
                break
    bot.reply_to(message, answer, parse_mode='Markdown')


@bot.message_handler(commands=['minet'])
def minet(message):
    """Приносит удовольствие"""
    log.logPrint(str(message.from_user.id)+": minet invoked")
    if not in_mf(message):
        return None
    if not cooldown(message):
        return None
    rep = choice(('оаоаоаоаооа мммммм)))))', 'Э, нет, эта кнопка не для тебя', 'Попа чистая?', 'Кусь :3',
                  'Открывай рот тогда)'))
    bot.reply_to(message, rep)


@bot.message_handler(commands=['uberminet'])
def uberminet(message):
    """ПРИНОСИТ УДОВОЛЬСТВИЕ"""
    log.logPrint(str(message.from_user.id)+": uberminet invoked")
    if not in_mf(message):
        return None
    if not cooldown(message):
        return None
    rep = choice(('оаоаоаоаооа мммммм)))))', 'Э, нет, эта кнопка не для тебя', 'Попа чистая?', 'Кусь :3',
                  'Открывай рот тогда)'))
    bot.reply_to(message, " *"+rep.upper()+"!!!!!*", parse_mode='Markdown')


@bot.message_handler(commands=['drakken'])
def send_drakken(message):
    """Присылает арт с Доктором Драккеном"""
    log.logPrint(str(message.from_user.id)+": send_drakken invoked")
    if not in_mf(message):
        return None
    if not cooldown(message):
        return None
    drakken = choice(('AgADAgADpqsxG3J5-Urrn-mZkdvjs1SnhQ8ABAEAAwIAA20AA9QNBAABFgQ',
                      'AgADAgADtaoxG3L2eUns8mJ7X9gm893qtw8ABAEAAwIAA20AA-gnAQABFgQ',
                      'AgADAgAD8asxG4SzgUm_RXHcgE4jd26xUQ8ABAEAAwIAA20AAzHIBQABFgQ',
                      'AgADAgAD06wxG6uiUEkjcLfrDsigh339tw8ABAEAAwIAA20AA8f_AAIWBA',
                      'AgADAgAD36oxG0ImAUvzgBI4oR5C9J_RuQ8ABAEAAwIAA20AA9FGAQABFgQ',
                      'AgADAgADRKoxG1QCQUmlG28vrK8o_avCtw8ABAEAAwIAA20AA8v1AAIWBA'))
    bot.send_photo(message.chat.id, drakken, reply_to_message_id=message.message_id)


@bot.message_handler(regexp='есть один мем')
@bot.message_handler(commands=['meme'])
def send_meme(message):
    """Присылает мем про третью руку"""
    
    log.logPrint(str(message.from_user.id)+": send_meme invoked")
    if not in_mf(message):
        return None
    if not cooldown(message):
        return None
    meme = choice(('AgADAgADx60xG2S_oUmVz41Dk8a4AkRNUw8ABAEAAwIAA20AAzj4BQABFgQ',
                   'AgADAgADdKsxG7PUsEmfWmu7wYQaSlHNuQ8ABAEAAwIAA20AA2gAAxYE',
                   'AgADAgAD-aoxG0EnIUqnHKx1l-EFFajiug8ABAEAAwIAA20AA3VUAAIWBA',
                   'AgADAgADY6sxG2RPyUmfTbFEJLvRV9Lhtw8ABAEAAwIAA20AA-lxAQABFgQ',
                   'AgADAgAD36sxG3h0uUlOXJnN-wooZiGxhQ8ABAEAAwIAA3gAA7nOAgABFgQ',
                   'AgADAgADJKsxG-KVuElBSmME_b_Cn8KghQ8ABAEAAwIAA20AA2DOAgABFgQ'))
    bot.send_photo(message.chat.id, meme, reply_to_message_id=message.message_id)


@bot.message_handler(commands=['me'], func=lambda message: in_mf(message))
def send_me(message):
    """Присылает человеку его запись в БД"""
    
    log.logPrint(str(message.from_user.id)+": send_me invoked")
    database = Database()
    person = database.get(message.from_user.id)
    msg = 'ID: {}\n'.format(person[0])
    msg += 'Юзернейм: {}\n'.format(person[1])
    msg += 'Никнейм: {}\n'.format(person[2])
    msg += 'Ранг: {}\n'.format(person[3])
    msg += 'Кол-во сообщений: {}\n'.format(person[4])
    msg += 'Кол-во предупреждений: {}\n'.format(person[5])
    msg += 'Количество ябломилианов: {}\n'.format(person[6])
    bot.reply_to(message, msg)
    del database
