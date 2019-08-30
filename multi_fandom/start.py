# -*- coding: utf-8 -*-
from multi_fandom.config.config_var import *
start_work = True


def new_option(message):

    file = open("multi_fandom/shelve/upgraders.txt")
    upgraders = eval(file.read())  # Словарик улучшителей вида {айди челика: айди улучшаемой голосовашки}
    file.close()
    vote_id = upgraders[message.from_user.id]

    del upgraders[message.from_user.id]
    file = open("multi_fandom/shelve/upgraders.txt", 'w')
    file.write(str(upgraders))
    file.close()

    bot.send_message(381279599, "[{}, '{}']".format(vote_id, message.text), reply_markup=adequate_keyboard)
    bot.reply_to(message, "Ваше мнение выслано на проверку")


def new_adapt_option(message):

    file = open("multi_fandom/shelve/adapt_upgraders.txt")
    upgraders = eval(file.read())  # Словарик улучшителей вида {айди челика: айди улучшаемой голосовашки}
    file.close()
    vote_id = upgraders[message.from_user.id]

    del upgraders[message.from_user.id]
    file = open("multi_fandom/shelve/adapt_upgraders.txt", 'w')
    file.write(str(upgraders))
    file.close()

    bot.send_message(381279599, "[{}, '{}']".format(vote_id, message.text), reply_markup=a_adequate_keyboard)
    bot.reply_to(message, "Ваше мнение выслано на проверку")


@bot.message_handler(commands=['start'])
def starter(message):
    """Запуск бота в личке, в чате просто реагирует"""
    print(message.text)
    if not in_mf(message):
        return None
    if "full_rules" in message.text:
        bot.reply_to(message, open("multi_fandom/full_rules.txt").read(), parse_mode="Markdown")
    elif "elitocracy" in message.text:
        bot.reply_to(message, open("multi_fandom/elitocracy.txt").read(), parse_mode="Markdown")
    elif "etiquette" in message.text:
        bot.reply_to(message, open("multi_fandom/etiquette.txt").read(), parse_mode="Markdown")
    elif "ranks" in message.text:
        bot.reply_to(message, open("multi_fandom/ranks.txt").read(), parse_mode="Markdown")
    elif "new_option" in message.text:
        file = open("multi_fandom/shelve/upgraders.txt")
        votes_shelve = file.read()
        if votes_shelve:
            votes_shelve = eval(votes_shelve)
        else:
            votes_shelve = {}
        file.close()
        votes_shelve[message.from_user.id] = int(message.text[17:])
        file = open("multi_fandom/shelve/upgraders.txt", 'w')
        file.write(str(votes_shelve))
        file.close()
        sent = bot.reply_to(message, "Введите ваш вариант ответа на голосовании")
        bot.register_next_step_handler(sent, new_option)
    elif "new_adapt_option" in message.text:
        file = open("multi_fandom/shelve/adapt_upgraders.txt")
        votes_shelve = file.read()
        if votes_shelve:
            votes_shelve = eval(votes_shelve)
        else:
            votes_shelve = {}
        file.close()
        votes_shelve[message.from_user.id] = int(message.text[23:])
        file = open("multi_fandom/shelve/adapt_upgraders.txt", 'w')
        file.write(str(votes_shelve))
        file.close()
        sent = bot.reply_to(message, "Введите ваш вариант ответа на голосовании")
        bot.register_next_step_handler(sent, new_adapt_option)
    else:
        bot.reply_to(message, "Здравствуй. Для получения всех существующих функций нажми /help")
