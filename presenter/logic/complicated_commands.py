# -*- coding: utf-8 -*-
from presenter.config.config_func import update_adapt_vote, update_multi_vote, create_adapt_vote, create_vote, \
    create_multi_vote, remove_captcher, kick_and_unban
from presenter.config.config_var import test_keyboard, ironic_keyboard, \
    vote_keyboard, admin_place
from presenter.config.database_lib import Database
from presenter.config.files_paths import multi_votes_file, adapt_votes_file, votes_file
from view.output import edit_markup, answer_inline, reply, answer_callback, edit_text, delete, send, restrict
from presenter.config.log import Loger, log_to

from telebot.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from time import time

log = Loger(log_to)
work = True


def captcha_completed(call):
    log.log_print("captcha_completed invoked")
    if remove_captcher(call):
        restrict(call.message.chat.id, call.from_user.id, can_send_messages=True, can_send_other_messages=True,
                 can_send_media_messages=True, can_add_web_page_previews=True)
        answer_callback(call.id, text='Испытание креветкой пройдено!')
        edit_markup(call.message.chat.id, call.message.message_id)
    else:
        answer_callback(call.id, text='Это не ваша креветка 👀')


def captcha_failed(call):
    log.log_print("captcha_failed invoked")
    if remove_captcher(call):
        kick_and_unban(call.message.chat.id, call.from_user.id)
        answer_callback(call.id)
        edit_text("Испытание креветкой провалено! (нажата неверная кнопка)", call.message.chat.id,
                  call.message.message_id)
    else:
        answer_callback(call.id, text='Это не ваша животинка 👀')


def adequate(call):
    """Вариант адекватен"""
    log.log_print("adequate invoked")
    file_place = None
    if call.data == 'adequate':
        file_place = multi_votes_file
    elif call.data == 'a_adequate':
        file_place = adapt_votes_file
    file = open(file_place, encoding='utf-8')
    votes_shelve = eval(file.read())
    info = eval(call.message.text)
    vote_id = info[0]
    votey = votes_shelve[vote_id]  # Получаем необходимую нам голосовашку в хранилище
    votey["keyboard"].append(info[1])
    votey["votes"].append([info[1], {}])  # Добавляем вариант
    votes_shelve[vote_id] = votey
    file = open(file_place, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    if call.data == 'adequate':
        update_multi_vote(vote_id)
    elif call.data == 'a_adequate':
        update_adapt_vote(vote_id)
    edit_markup(call.message.chat.id, call.message.message_id)


def inadequate(call):
    """Вариант неадекватен"""
    log.log_print("inadequate invoked")
    edit_markup(call.message.chat.id, call.message.message_id)


def response(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    log.log_print("response invoked")
    results = [InlineQueryResultArticle('1', 'Тестовый заголовок', InputTextMessageContent("Тестовый текст"),
                                        reply_markup=test_keyboard)]
    answer_inline(inline_query.id, results=results, cache_time=1)


def insult(message):
    """Спращивает, иронично ли признание оскорблением"""
    log.log_print("insult invoked")
    text = "Иронично? \n\n(В случае нажатия 'Неиронично' в админосостав будет послана жалоба. Будьте добры не пользоваться каналом жалоб, если вас не оскорбили)"
    reply(message, text, reply_markup=ironic_keyboard)


def non_ironic(call):
    """Реакция, если обвинение было неироничным"""
    log.log_print("non_ironic invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    edit_text("Неиронично!", call.message.chat.id, call.message.message_id)
    # TODO добавить сюда голосовашку
    send(admin_place(call.message, Database()),
         "Произошло оскорбление! " +
         "[Ссылка на инцидент](t.me/{}/{})".format(call.message.reply_to_message.chat.username,
                                                   call.message.reply_to_message.message_id),
         parse_mode="Markdown", disable_web_page_preview=True)
    try:
        answer_callback(call.id)
    except Exception as e:
        print(e)


def ironic(call):
    """Реакция, если обвинение было ироничным"""
    log.log_print("ironic invoked")
    edit_text("Иронично, так иронично", call.message.chat.id, call.message.message_id)
    answer_callback(call.id)


def place_here(call):
    """Выбирает, куда прислать голосовашку"""
    log.log_print("place_here invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    where = None
    if call.data == 'here' or call.data == 'm_here' or call.data == 'a_here':
        where = call.message.chat.id
    elif call.data == 'there' or call.data == 'm_there' or call.data == 'a_there':
        where = -1001260953849  # Канал голосовашек
    elif 'nedostream' in call.data:
        where = -1001409685984  # Канал недостримов
    if call.message.reply_to_message.text.split()[0] == '/vote':
        vote_message = send(where, 'Голосование "{}"'
                            .format(call.message.reply_to_message.text[6:]), reply_markup=vote_keyboard)
        create_vote(vote_message)
    elif call.message.reply_to_message.text.split()[0] == '/multi_vote':
        answer = 'Мульти-голосование (вы можете предлагать варианты и выбирать несколько ответов)\n\n"{}"\n'
        vote_message = send(where, answer.format(call.message.reply_to_message.text[12:]))
        create_multi_vote(vote_message)
    elif call.message.reply_to_message.text.split()[0] == '/adapt_vote':
        answer = 'Адапт-голосование (вы можете предлагать варианты, но выбирать только 1 вариант)\n\n"{}"\n'
        vote_message = send(where, answer.format(call.message.reply_to_message.text[12:]))
        create_adapt_vote(vote_message)
    delete(call.message.chat.id, call.message.message_id)


def mv(call):
    """Обновляет мульти-голосовашку"""
    log.log_print("mv invoked")
    user = call.from_user
    user_username = user.username  # юзернейм жмакнувшего челика
    user_nickname = user.first_name
    user_id = user.id
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    link = f'<a href="t.me/{user_username}">{user_nickname}</a>'
    which = int(call.data[-1])  # Где менять мнение
    file = open(multi_votes_file, encoding='utf-8')
    votes_shelve = eval(file.read())
    votey = votes_shelve[msg_id]  # Получаем необходимую нам голосовашку в хранилище
    file.close()

    if user_id in votey['votes'][which][1].keys():  # Челик нажал на кнопку, на которой есть его мнение
        # удаляем челика из словаря
        votey['votes'][which][1].pop(user_id)  # TODO Убрать быдлокод такого вида, изменив структуру МГ и АГ
    else:
        # если чедика нету - то просто добавляем
        votey['votes'][which][1].update([(user_id, link)])
    # Сохраняем изменения
    votes_shelve[msg_id] = votey
    file = open(multi_votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    answer_callback(call.id, text="Жмак учтён!")
    update_multi_vote(call.message.message_id)  # TODO возможность стопнуть мульти-голосовашку


def av(call):
    """Обновляет адапт-голосовашку"""
    log.log_print("av invoked")
    user = call.from_user
    user_username = user.username  # юзернейм жмакнувшего челика
    user_nickname = user.first_name
    user_id = user.id
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    link = f'<a href="t.me/{user_username}">{user_nickname}</a>'
    which = int(call.data[-1])  # Где менять мнение
    file = open(adapt_votes_file, encoding='utf-8')
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
            votey['votes'][which][1].update([(user_id, link)])
    # Сохраняем изменения
    votes_shelve[msg_id] = votey
    file = open(adapt_votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    answer_callback(call.id, text="Жмак учтён!")
    update_adapt_vote(call.message.message_id)  # TODO возможность стопнуть адапт-голосовашку


def add_vote(call):
    """Вставляет голос в голосоовашку"""
    log.log_print("add_vote invoked")
    reply_markup = vote_keyboard
    text = ''
    user = call.from_user
    user_username = user.username  # юзернейм жмакнувшего челика
    user_nickname = user.first_name
    user_id = user.id
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    link = f'<a href="t.me/{user_username}">{user_nickname}</a>'
    file = open(votes_file, 'r', encoding='utf-8')
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
            votey[call.data].update([(user_id, link)])
        votes_shelve[msg_id] = votey
        text += votey["text"]
        text += '\nЗа: ' + ', '.join(votey["favor"].values())
        text += '\nПротив: ' + ', '.join(votey["against"].values())
        text += '\nВоздерживающиеся: ' + ', '.join(votey["abstain"].values())
    else:
        reply_markup = None
        text += 'Голосование окончено по причине ненахода записи об этой голосовашки. Новые голоса не принимаются\n\n'
        text += call.message.text
    file = open(votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    edit_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id,
              reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
    answer_callback(call.id, text="Жмак учтён!")


def vote(message):
    log.log_print(f'{__name__} invoked')
    where_keyboard = InlineKeyboardMarkup()
    where_keyboard.row_width = 1
    where_keyboard.add(InlineKeyboardButton("Сюда", callback_data="here"))
    '''
    if appointment_required(message, 'Admin', loud=False):
        where_keyboard.add(InlineKeyboardButton("На канал голосовашек", callback_data="there"))
    if appointment_required(message, 'Content-maker', loud=False):
        where_keyboard.add(InlineKeyboardButton("На канал недостримов", callback_data="nedostream"))
    '''
    reply(message, "А запостить куда?", reply_markup=where_keyboard)

# TODO разделить этот модуль на сообщения с кнопками и триггеры кнопок
