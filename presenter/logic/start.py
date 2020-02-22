# -*- coding: utf-8 -*-
"""Special module for all /start commands"""
from view.output import send, reply, register_handler
from presenter.config.log import Loger, log_to
import presenter.config.files_paths as files
from presenter.config.config_var import ADEQUATE_KEYBOARD, ADAPT_ADEQUATE_KEYBOARD
from presenter.config.config_func import language_analyzer

WORK = True

LOG = Loger(log_to)


def new_option(message, vote_id):
    """Send option to De'Max to check if it's adequate"""
    LOG.log_print(str(message.from_user.id) + ": new_option invoked")
    send(381279599, "[{}, '{}']".format(vote_id, message.text), reply_markup=ADEQUATE_KEYBOARD)
    reply(message, "Ваше мнение выслано на проверку")


def new_adapt_option(message, vote_id):
    """Send option to De'Max to check if it's adequate"""
    LOG.log_print(str(message.from_user.id) + ": new_adapt_option invoked")
    send(381279599, "[{}, '{}']".format(vote_id, message.text), reply_markup=ADAPT_ADEQUATE_KEYBOARD)
    reply(message, "Ваше мнение выслано на проверку")


def starter(message):
    """Запуск бота в личке, в чате просто реагирует"""
    LOG.log_print(str(message.from_user.id) + ": starter invoked")
    if "full_rules" in message.text:
        reply(message, open(files.FULL_RULES, encoding='utf-8').read(), parse_mode="Markdown")
    elif "elitocracy" in message.text:
        reply(message, open(files.ELITOCRACY, encoding='utf-8').read(), parse_mode="Markdown")
    elif "etiquette" in message.text:
        reply(message, open(files.ETIQUETTE, encoding='utf-8').read(), parse_mode="Markdown")
    elif "ranks" in message.text:
        reply(message, open(files.RANKS, encoding='utf-8').read(), parse_mode="Markdown")
    elif "appointments" in message.text:
        reply(message, open(files.APPOINTMENTS, encoding='utf-8').read(), parse_mode="Markdown")
    elif "new_option" in message.text:
        vote_id = int(message.text.split('new_option')[1])
        sent = reply(message, "Введите ваш вариант ответа на голосовании")
        register_handler(sent, new_option, vote_id)
    elif "new_adapt_option" in message.text:
        vote_id = int(message.text.split('new_adapt_option')[1])
        sent = reply(message, "Введите ваш вариант ответа на голосовании")
        register_handler(sent, new_adapt_option, vote_id)
    else:
        languages = language_analyzer(message, only_one=False)
        text = ''
        if languages['English']:
            text += "Hello. To get all existing functions click /help\n\n"
        if languages['Russian']:
            text += "Здравствуй. Для получения всех существующих функций нажми /help\n\n"
        reply(message, text)
