# -*- coding: utf-8 -*-
from multi_fandom.config.config_var import *
from time import time
complicated_commands_work = True


@bot.callback_query_handler(func=lambda call: 'adequate' in call.data)
def adequate(call):
    """Вариант адекватен"""
    file_place = None
    if call.data == 'adequate':
        file_place = "multi_fandom/shelve/multi_votes.txt"
    elif call.data == 'a_adequate':
        file_place = "multi_fandom/shelve/adapt_votes.txt"
    file = open(file_place)
    votes_shelve = eval(file.read())
    info = eval(call.message.text)
    vote_id = info[0]
    votey = votes_shelve[vote_id]  # Получаем необходимую нам голосовашку в хранилище
    votey["keyboard"].append(info[1])
    votey["votes"].append([info[1], {}])  # Добавляем вариант
    votes_shelve[vote_id] = votey
    file = open(file_place, 'w')
    file.write(str(votes_shelve))
    file.close()
    if call.data == 'adequate':
        update_multi_vote(vote_id)
    elif call.data == 'a_adequate':
        update_adapt_vote(vote_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'inadequate')
def inadequate(call):
    """Вариант неадекватен"""
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


@bot.inline_handler(lambda query: query.query == 'test')
def response(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    results = [telebot.types.InlineQueryResultArticle('1', 'Тестовый заголовок',
                                                      telebot.types.InputTextMessageContent("Тестовый текст"),
                                                      reply_markup=test_keyboard)]
    bot.answer_inline_query(inline_query.id, results=results, cache_time=1)


@bot.message_handler(regexp='Признаю оскорблением')
def insult(message):
    """Спращивает, иронично ли признание оскорблением"""
    if not in_mf(message, False):
        return None
    text = "Иронично? \n\n(обращаем ваше внимание на то, что если вы по приколу нажмёте на 'нет', то "
    text += "ваши действия могут быть сочтены админами, как провокация)"
    bot.reply_to(message, text, reply_markup=ironic_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'non_ironic')  # триггерится, когда нажата кнопка "Нет"
def non_ironic(call):
    """Реакция, если обвинение было неироничным"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id != call.from_user.id:
        bot.answer_callback_query(call.id, "Э, нет, эта кнопка не для тебя")
        return None
    bot.edit_message_text("Неиронично!", call.message.chat.id, call.message.message_id)
    database = Database()
    admins = database.get("Админосостав", "chats", "purpose")[0]  # Получаем ай ди нынешнего админосостава
    # TODO добавить сюда голосовашку
    bot.send_message(admins, "Если вы это читаете, то разработка авто-признавалки оскорблений проходит хорошо " +
                     "[Ссылка на инцидент](t.me/{}/{})".format(call.message.reply_to_message.chat.username,
                                                               call.message.reply_to_message.message_id),
                     parse_mode="Markdown", disable_web_page_preview=True)
    try:
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data == 'ironic')  # триггерится, когда нажата кнопка "Да"
def ironic(call):
    """Реакция, если обвинение было ироничным"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id != call.from_user.id:
        bot.answer_callback_query(call.id, "Э, нет, эта кнопка не для тебя")
        return None
    bot.edit_message_text("Иронично, так иронично", call.message.chat.id, call.message.message_id)
    try:
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['vote', 'multi_vote', 'adapt_vote'])
def vote(message):
    """Генерирует голосовашку"""
    if not in_mf(message):
        return None
    database = Database()
    rank = database.get(message.from_user.id)[3]  # Получаем его звание
    if rank != "Админ" and rank != "Член Комитета" and rank != "Заместитель" and rank != "Лидер":
        bot.reply_to(message, "Э, нет, эта кнопка только для админов")
        return None
    reply_markup = None
    if '/vote' in message.text:
        reply_markup = where_keyboard
    elif '/multi_vote' in message.text:
        reply_markup = m_where_keyboard
    elif '/adapt_vote' in message.text:
        reply_markup = a_where_keyboard
    bot.reply_to(message, 'А запостить куда?', reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: 'here' in call.data)
def place_here(call):
    """Выбирает, куда прислать голосовашку"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id != call.from_user.id:
        bot.answer_callback_query(call.id, "Э, нет, эта кнопка не для тебя")
        return None
    where = None
    if call.data == 'here' or call.data == 'm_here' or call.data == 'a_here':
        where = call.message.chat.id
    elif call.data == 'there' or call.data == 'm_there' or call.data == 'a_there':
        where = -1001260953849  # Канал голосовашек
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == 'here' or call.data == 'there':
        vote_message = bot.send_message(where, 'Голосование "{}"'
                                        .format(call.message.reply_to_message.text[6:]), reply_markup=vote_keyboard)
        create_vote(vote_message)
    elif call.data == 'm_here' or call.data == 'm_there':
        answer = 'Мульти-голосование (вы можете предлагать варианты и выбирать несколько ответов)\n\n"{}"\n'
        vote_message = bot.send_message(where, answer.format(call.message.reply_to_message.text[12:]))
        create_multi_vote(vote_message)
    elif call.data == 'a_here' or call.data == 'a_there':
        answer = 'Адапт-голосование (вы можете предлагать варианты, но выбирать только 1 вариант)\n\n"{}"\n'
        vote_message = bot.send_message(where, answer.format(call.message.reply_to_message.text[12:]))
        create_adapt_vote(vote_message)


@bot.callback_query_handler(func=lambda call: 'mv_' in call.data)
def mv(call):
    """Обновляет мульти-голосовашку"""
    user_id = str(call.from_user.id)  # Ай ди жмакнувшего челика
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    username = "[{}](tg://user?id={})".format(call.from_user.first_name.replace('[', '').replace(']', ''), user_id)
    which = int(call.data[-1])  # Где менять мнение
    file = open("multi_fandom/shelve/multi_votes.txt")
    votes_shelve = eval(file.read())
    votey = votes_shelve[msg_id]  # Получаем необходимую нам голосовашку в хранилище
    file.close()

    if user_id in votey['votes'][which][1].keys():  # Челик нажал на кнопку, на которой есть его мнение
        # удаляем челика из словаря
        votey['votes'][which][1].pop(user_id)
    else:
        # если чедика нету - то просто добавляем
        votey['votes'][which][1].update([(user_id, username)])
    # Сохраняем изменения
    votes_shelve[msg_id] = votey
    file = open("multi_fandom/shelve/multi_votes.txt", 'w')
    file.write(str(votes_shelve))
    file.close()
    bot.answer_callback_query(call.id, text="Жмак учтён!")
    update_multi_vote(call.message.message_id)  # TODO возможность стопнуть мульти-голосовашку


@bot.callback_query_handler(func=lambda call: 'av_' in call.data)
def av(call):
    """Обновляет адапт-голосовашку"""
    user_id = str(call.from_user.id)  # Ай ди жмакнувшего челика
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    username = "[{}](tg://user?id={})".format(call.from_user.first_name.replace('[', '').replace(']', ''), user_id)
    which = int(call.data[-1])  # Где менять мнение
    file = open("multi_fandom/shelve/adapt_votes.txt")
    votes_shelve = eval(file.read())
    votey = votes_shelve[msg_id]  # Получаем необходимую нам голосовашку в хранилище
    file.close()
    if msg_id in votes_shelve.keys():
        if user_id in votey['votes'][which][1].keys():  # Челик нажал на кнопку, на которой есть его мнение
            # удаляем челика из словаря
            votey['votes'][which][1].pop(user_id)
        else:
            for i in votey['votes']:
                i[1].pop(user_id, None)
            # если чедика нету - то просто добавляем
            votey['votes'][which][1].update([(user_id, username)])
    # Сохраняем изменения
    votes_shelve[msg_id] = votey
    file = open("multi_fandom/shelve/adapt_votes.txt", 'w')
    file.write(str(votes_shelve))
    file.close()
    bot.answer_callback_query(call.id, text="Жмак учтён!")
    update_adapt_vote(call.message.message_id)  # TODO возможность стопнуть адапт-голосовашку


@bot.callback_query_handler(func=lambda call: call.data == 'favor' or call.data == 'against' or call.data == 'abstain')
def add_vote(call):
    """Вставляет голос в голосоовашку"""
    reply_markup = vote_keyboard
    text = ''
    user_id = call.from_user.id  # Ай ди жмакнувшего челика
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    username = "[{}](tg://user?id={})".format(call.from_user.first_name.replace('[', '').replace(']', ''), user_id)
    file = open("multi_fandom/shelve/votes.txt", 'r')
    votes_shelve = eval(file.read())
    file.close()
    if msg_id in votes_shelve.keys():
        votey = votes_shelve[msg_id]  # Получаем необходимую нам голосовашку в хранилище
        if time() - votey['time'] > 86400 and len(votey['favor']) != len(votey['against']):  # это сутки
            reply_markup = None
            text += 'Голосование окончено. Новые голоса не принимаются\n\n'
        elif user_id in votey[call.data].keys():  # Челик нажал на кнопку, на которой есть его мнение
            # удаляем челика из словаря
            votey[call.data].pop(user_id)
        else:
            # Чистим прошлые мнения челика и записываем новое
            votey['favor'].pop(user_id, None)
            votey['against'].pop(user_id, None)
            votey['abstain'].pop(user_id, None)
            votey[call.data].update([(user_id, username)])
        votes_shelve[msg_id] = votey
        text += votey["text"]
        text += '\nЗа: ' + ', '.join(votey["favor"].values())
        text += '\nПротив: ' + ', '.join(votey["against"].values())
        text += '\nВоздерживающиеся: ' + ', '.join(votey["abstain"].values())
    else:
        reply_markup = None
        text += 'Голосование окончено по причине ненахода записи об этой голосовашки. Новые голоса не принимаются\n\n'
        text += call.message.text
    file = open("multi_fandom/shelve/votes.txt", 'w')
    file.write(str(votes_shelve))
    file.close()
    try:  # Меняем текст голосовашки
        bot.edit_message_text(text=text,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=reply_markup,
                              parse_mode="Markdown")
        bot.answer_callback_query(call.id, text="Жмак учтён!")
    except Exception as e:
        print(e)


# TODO Голосовашки только для граждан
# TODO разделить этот модуль на сообщения с кнопками и триггеры кнопок
