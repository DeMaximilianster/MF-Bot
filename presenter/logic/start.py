# -*- coding: utf-8 -*-
from view.output import send, reply, register_handler
from presenter.config.log import Loger, log_to
from presenter.config.files_paths import *
from presenter.config.config_var import adequate_keyboard, a_adequate_keyboard

start_work = True

log = Loger(log_to)


def new_option(message, vote_id):
    log.log_print(str(message.from_user.id) + ": new_option invoked")
    send(381279599, "[{}, '{}']".format(vote_id, message.text), reply_markup=adequate_keyboard)
    reply(message, "Ваше мнение выслано на проверку")


def new_adapt_option(message, vote_id):
    log.log_print(str(message.from_user.id) + ": new_adapt_option invoked")
    send(381279599, "[{}, '{}']".format(vote_id, message.text), reply_markup=a_adequate_keyboard)
    reply(message, "Ваше мнение выслано на проверку")


def starter(message, lang):
    """Запуск бота в личке, в чате просто реагирует"""
    log.log_print(str(message.from_user.id) + ": starter invoked")
    if "full_rules" in message.text:
        reply(message, open(full_rules).read(), parse_mode="Markdown")
    elif "elitocracy" in message.text:
        reply(message, open(elitocracy).read(), parse_mode="Markdown")
    elif "etiquette" in message.text:
        reply(message, open(etiquette).read(), parse_mode="Markdown")
    elif "ranks" in message.text:
        reply(message, open(ranks).read(), parse_mode="Markdown")
    elif "appointments" in message.text:
        reply(message, open(appointments).read(), parse_mode="Markdown")
    elif "new_option" in message.text:
        vote_id = int(message.text.split('new_option')[1])
        sent = reply(message, "Введите ваш вариант ответа на голосовании")
        register_handler(sent, new_option, vote_id)
    elif "new_adapt_option" in message.text:
        vote_id = int(message.text.split('new_adapt_option')[1])
        sent = reply(message, "Введите ваш вариант ответа на голосовании")
        register_handler(sent, new_adapt_option, vote_id)
    else:
        text = ''
        if lang['en']:
            text += "Hello. To get all existing functions click /help\n\n"
        if lang['ru']:
            text += "Здравствуй. Для получения всех существующих функций нажми /help\n\n"
        reply(message, text)
