# -*- coding: utf-8 -*-
from view.output import send, reply, register_handler
from presenter.config.log import Loger, log_to
from presenter.config.files_paths import *
from presenter.config.config_var import adequate_keyboard, a_adequate_keyboard
start_work = True

log = Loger(log_to)


def new_option(message):
    log.log_print(str(message.from_user.id)+": new_option invoked")
    file = open(upgraders_file, encoding='utf-8')  # TODO файл upgraders.txt это чистое воплощение быдлокода
    upgraders = eval(file.read())  # Словарик улучшителей вида {айди челика: айди улучшаемой голосовашки}
    file.close()
    vote_id = upgraders[message.from_user.id]

    del upgraders[message.from_user.id]
    file = open(upgraders_file, 'w', encoding='utf-8')
    file.write(str(upgraders))
    file.close()

    send(381279599, "[{}, '{}']".format(vote_id, message.text), reply_markup=adequate_keyboard)
    reply(message, "Ваше мнение выслано на проверку")


def new_adapt_option(message):
    log.log_print(str(message.from_user.id)+": new_adapt_option invoked")

    file = open(adapt_upgraders_file, encoding='utf-8')
    upgraders = eval(file.read())  # Словарик улучшителей вида {айди челика: айди улучшаемой голосовашки}
    file.close()
    vote_id = upgraders[message.from_user.id]

    del upgraders[message.from_user.id]
    file = open(adapt_upgraders_file, 'w', encoding='utf-8')
    file.write(str(upgraders))
    file.close()

    send(381279599, "[{}, '{}']".format(vote_id, message.text), reply_markup=a_adequate_keyboard)
    reply(message, "Ваше мнение выслано на проверку")


def starter(message):
    """Запуск бота в личке, в чате просто реагирует"""
    log.log_print(str(message.from_user.id)+": starter invoked")
    print(message.text)
    if "full_rules" in message.text:
        reply(message, open(full_rules).read(), parse_mode="Markdown")
    elif "elitocracy" in message.text:
        reply(message, open(elitocracy).read(), parse_mode="Markdown")
    elif "etiquette" in message.text:
        reply(message, open(etiquette).read(), parse_mode="Markdown")
    elif "ranks" in message.text:
        reply(message, open(ranks).read(), parse_mode="Markdown")
    elif "new_option" in message.text:
        file = open(upgraders_file, encoding='utf-8')
        votes_shelve = file.read()
        if votes_shelve:
            votes_shelve = eval(votes_shelve)
        else:
            votes_shelve = {}
        file.close()
        votes_shelve[message.from_user.id] = int(message.text[17:])
        file = open(upgraders_file, 'w', encoding='utf-8')
        file.write(str(votes_shelve))
        file.close()
        sent = reply(message, "Введите ваш вариант ответа на голосовании")
        register_handler(sent, new_option)
    elif "new_adapt_option" in message.text:
        file = open(adapt_upgraders_file, encoding='utf-8')
        votes_shelve = file.read()
        if votes_shelve:
            votes_shelve = eval(votes_shelve)
        else:
            votes_shelve = {}
        file.close()
        votes_shelve[message.from_user.id] = int(message.text[23:])
        file = open(adapt_upgraders_file, 'w', encoding='utf-8')
        file.write(str(votes_shelve))
        file.close()
        sent = reply(message, "Введите ваш вариант ответа на голосовании")
        register_handler(sent, new_adapt_option)
    else:
        reply(message, "Здравствуй. Для получения всех существующих функций нажми /help")
