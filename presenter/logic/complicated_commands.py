# -*- coding: utf-8 -*-
from presenter.config.config_func import update_adapt_vote, update_multi_vote, create_adapt_vote, create_vote, \
    create_multi_vote, Database
from presenter.config.config_var import test_keyboard, ironic_keyboard, m_where_keyboard, where_keyboard, \
    a_where_keyboard, vote_keyboard
from presenter.config.files_paths import multi_votes_file, adapt_votes_file, votes_file
from view.output import edit_markup, answer_inline, reply, answer_callback, edit_text, delete, send
import presenter.config.log as log

from telebot.types import InlineQueryResultArticle, InputTextMessageContent
from time import time

log = log.Loger(log.LOG_TO_CONSOLE)
work = True


def adequate(call):
    """Вариант адекватен"""
    file_place = None
    if call.data == 'adequate':
        file_place = multi_votes_file
    elif call.data == 'a_adequate':
        file_place = adapt_votes_file
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
    edit_markup(call.message.chat.id, call.message.message_id)


def inadequate(call):
    """Вариант неадекватен"""
    edit_markup(call.message.chat.id, call.message.message_id)


def response(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    results = [InlineQueryResultArticle('1', 'Тестовый заголовок', InputTextMessageContent("Тестовый текст"),
                                        reply_markup=test_keyboard)]
    answer_inline(inline_query.id, results=results, cache_time=1)


def insult(message):
    """Спращивает, иронично ли признание оскорблением"""
    text = "Иронично? \n\n(обращаем ваше внимание на то, что если вы по приколу нажмёте на 'нет', то "
    text += "ваши действия могут быть сочтены админами, как провокация)"
    reply(message, text, reply_markup=ironic_keyboard)


def non_ironic(call):
    """Реакция, если обвинение было неироничным"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    edit_text("Неиронично!", call.message.chat.id, call.message.message_id)
    database = Database()
    admins = database.get("Админосостав", "chats", "purpose")[0]  # Получаем ай ди нынешнего админосостава
    # TODO добавить сюда голосовашку
    send(admins, "Если вы это читаете, то разработка авто-признавалки оскорблений проходит хорошо " +
         "[Ссылка на инцидент](t.me/{}/{})".format(call.message.reply_to_message.chat.username,
                                                   call.message.reply_to_message.message_id),
         parse_mode="Markdown", disable_web_page_preview=True)
    try:
        answer_callback(call.id)
    except Exception as e:
        print(e)


def ironic(call):
    """Реакция, если обвинение было ироничным"""
    edit_text("Иронично, так иронично", call.message.chat.id, call.message.message_id)
    answer_callback(call.id)


def vote(message):
    """Генерирует голосовашку"""
    reply_markup = None
    if '/vote' in message.text:
        reply_markup = where_keyboard
    elif '/multi_vote' in message.text:
        reply_markup = m_where_keyboard
    elif '/adapt_vote' in message.text:
        reply_markup = a_where_keyboard
    reply(message, 'А запостить куда?', reply_markup=reply_markup)


def place_here(call):
    """Выбирает, куда прислать голосовашку"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    where = None
    if call.data == 'here' or call.data == 'm_here' or call.data == 'a_here':
        where = call.message.chat.id
    elif call.data == 'there' or call.data == 'm_there' or call.data == 'a_there':
        where = -1001260953849  # Канал голосовашек
    delete(call.message.chat.id, call.message.message_id)
    if call.data == 'here' or call.data == 'there':
        vote_message = send(where, 'Голосование "{}"'
                                   .format(call.message.reply_to_message.text[6:]), reply_markup=vote_keyboard)
        create_vote(vote_message)
    elif call.data == 'm_here' or call.data == 'm_there':
        answer = 'Мульти-голосование (вы можете предлагать варианты и выбирать несколько ответов)\n\n"{}"\n'
        vote_message = send(where, answer.format(call.message.reply_to_message.text[12:]))
        create_multi_vote(vote_message)
    elif call.data == 'a_here' or call.data == 'a_there':
        answer = 'Адапт-голосование (вы можете предлагать варианты, но выбирать только 1 вариант)\n\n"{}"\n'
        vote_message = send(where, answer.format(call.message.reply_to_message.text[12:]))
        create_adapt_vote(vote_message)


def mv(call):
    """Обновляет мульти-голосовашку"""
    user_id = str(call.from_user.id)  # Ай ди жмакнувшего челика
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    username = "[{}](tg://user?id={})".format(call.from_user.first_name.replace('[', '').replace(']', ''), user_id)
    which = int(call.data[-1])  # Где менять мнение
    file = open(multi_votes_file)
    votes_shelve = eval(file.read())
    votey = votes_shelve[msg_id]  # Получаем необходимую нам голосовашку в хранилище
    file.close()

    if user_id in votey['votes'][which][1].keys():  # Челик нажал на кнопку, на которой есть его мнение
        # удаляем челика из словаря
        votey['votes'][which][1].pop(user_id)   # TODO Убрать быдлокод такого вида, изменив структуру МГ и АГ
    else:
        # если чедика нету - то просто добавляем
        votey['votes'][which][1].update([(user_id, username)])
    # Сохраняем изменения
    votes_shelve[msg_id] = votey
    file = open(multi_votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()
    answer_callback(call.id, text="Жмак учтён!")
    update_multi_vote(call.message.message_id)  # TODO возможность стопнуть мульти-голосовашку


def av(call):
    """Обновляет адапт-голосовашку"""
    user_id = str(call.from_user.id)  # Ай ди жмакнувшего челика
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    username = "[{}](tg://user?id={})".format(call.from_user.first_name.replace('[', '').replace(']', ''), user_id)
    which = int(call.data[-1])  # Где менять мнение
    file = open(adapt_votes_file)
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
    file = open(adapt_votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()
    answer_callback(call.id, text="Жмак учтён!")
    update_adapt_vote(call.message.message_id)  # TODO возможность стопнуть адапт-голосовашку


def add_vote(call):
    """Вставляет голос в голосоовашку"""
    reply_markup = vote_keyboard
    text = ''
    user_id = call.from_user.id  # Ай ди жмакнувшего челика
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    username = "[{}](tg://user?id={})".format(call.from_user.first_name.replace('[', '').replace(']', ''), user_id)
    file = open(votes_file, 'r')
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
    file = open(votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()
    edit_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id,
              reply_markup=reply_markup, parse_mode="Markdown")
    answer_callback(call.id, text="Жмак учтён!")


# TODO Голосовашки только для граждан
# TODO разделить этот модуль на сообщения с кнопками и триггеры кнопок
