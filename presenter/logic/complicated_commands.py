"""Commands which involve creating and pushing buttons"""
# -*- coding: utf-8 -*-
from time import time
from ast import literal_eval
from telebot.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, \
    InlineKeyboardMarkup
from view.output import edit_markup, answer_inline, reply, \
    answer_callback, edit_text, delete, send, restrict
from presenter.config.config_func import update_adapt_vote, update_multi_vote, create_adapt_vote, \
    create_vote, create_multi_vote, remove_captcher, kick_and_unban
from presenter.config.config_var import TEST_KEYBOARD, IRONIC_KEYBOARD, \
    VOTE_KEYBOARD, admin_place
from presenter.config.database_lib import Database
from presenter.config.files_paths import MULTI_VOTES_FILE, ADAPT_VOTES_FILE, VOTES_FILE
from presenter.config.log import Logger, log_to


LOG = Logger(log_to)
WORK = True


def captcha_completed(call):
    """Bot reacts to someone clicked correct button"""
    LOG.log_print("captcha_completed invoked")
    if remove_captcher(call):
        restrict(call.message.chat.id,
                 call.from_user.id,
                 can_send_messages=True,
                 can_send_other_messages=True,
                 can_send_media_messages=True,
                 can_add_web_page_previews=True)
        answer_callback(call.id, text='Испытание креветкой пройдено!')
        edit_markup(call.message.chat.id, call.message.message_id)
        # TODO Менять текст сообщения на текст-приветствие при выключенной капче
    else:
        answer_callback(call.id, text='Это не ваша креветка 👀')


def captcha_failed(call):
    """Bot reacts to someone clicked wrong button"""
    LOG.log_print("captcha_failed invoked")
    if remove_captcher(call):
        kick_and_unban(call.message.chat.id, call.from_user.id)
        answer_callback(call.id)
        edit_text("Испытание креветкой провалено! (нажата неверная кнопка)", call.message.chat.id,
                  call.message.message_id)
    else:
        answer_callback(call.id, text='Это не ваша животинка 👀')


def adequate(call):
    """Вариант адекватен"""
    LOG.log_print("adequate invoked")
    file_place = None
    if call.data == 'adequate':
        file_place = MULTI_VOTES_FILE
    elif call.data == 'a_adequate':
        file_place = ADAPT_VOTES_FILE
    file = open(file_place, encoding='utf-8')
    votes_shelve = literal_eval(file.read())
    info = literal_eval(call.message.text)
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
    LOG.log_print("inadequate invoked")
    edit_markup(call.message.chat.id, call.message.message_id)


def response(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    LOG.log_print("response invoked")
    results = [
        InlineQueryResultArticle('1',
                                 'Тестовый заголовок',
                                 InputTextMessageContent("Тестовый текст"),
                                 reply_markup=TEST_KEYBOARD)
    ]
    answer_inline(inline_query.id, results=results, cache_time=1)


def insult(message):
    """Спращивает, иронично ли признание оскорблением"""
    LOG.log_print("insult invoked")
    text = "Иронично? \n\n(В случае нажатия 'Неиронично' в админосостав будет послана жалоба. " \
           "Будьте добры не пользоваться каналом жалоб, если вас не оскорбили)"
    reply(message, text, reply_markup=IRONIC_KEYBOARD)


def non_ironic(call):
    """Реакция, если обвинение было неироничным"""
    LOG.log_print("non_ironic invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    edit_text("Неиронично!", call.message.chat.id, call.message.message_id)
    # TODO добавить сюда голосовашку
    send(admin_place(call.message, Database()),
         "Произошло оскорбление! " + "[Ссылка на инцидент](t.me/{}/{})".format(
             call.message.reply_to_message.chat.username, call.message.reply_to_message.message_id),
         parse_mode="Markdown")
    answer_callback(call.id)


def ironic(call):
    """Реакция, если обвинение было ироничным"""
    LOG.log_print("ironic invoked")
    edit_text("Иронично, так иронично", call.message.chat.id, call.message.message_id)
    answer_callback(call.id)


def place_here(call):
    """Выбирает, куда прислать голосовашку"""
    LOG.log_print("place_here invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    where = None
    if call.data == 'here' or call.data == 'm_here' or call.data == 'a_here':
        where = call.message.chat.id
    elif call.data == 'there' or call.data == 'm_there' or call.data == 'a_there':
        where = -1001260953849  # Канал голосовашек
    elif 'nedostream' in call.data:
        where = -1001409685984  # Канал недостримов
    if call.message.reply_to_message.text.split()[0] == '/vote':
        vote_message = send(where,
                            'Голосование "{}"'.format(call.message.reply_to_message.text[6:]),
                            reply_markup=VOTE_KEYBOARD)
        create_vote(vote_message)
    elif call.message.reply_to_message.text.split()[0] == '/multi_vote':
        answer = 'Мульти-голосование (вы можете предлагать варианты ' \
                 'и выбирать несколько ответов)\n\n"{}"\n'
        vote_message = send(where, answer.format(call.message.reply_to_message.text[12:]))
        create_multi_vote(vote_message)
    elif call.message.reply_to_message.text.split()[0] == '/adapt_vote':
        answer = 'Адапт-голосование (вы можете предлагать варианты, ' \
                 'но выбирать только 1 вариант)\n\n"{}"\n'
        vote_message = send(where, answer.format(call.message.reply_to_message.text[12:]))
        create_adapt_vote(vote_message)
    delete(call.message.chat.id, call.message.message_id)


def multi_vote(call):
    """Обновляет мульти-голосовашку"""
    LOG.log_print("mv invoked")
    user = call.from_user
    user_username = user.username  # юзернейм жмакнувшего челика
    user_nickname = user.first_name
    user_id = user.id
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    link = f'<a href="t.me/{user_username}">{user_nickname}</a>'
    which = int(call.data[-1])  # Где менять мнение
    file = open(MULTI_VOTES_FILE, encoding='utf-8')
    votes_shelve = literal_eval(file.read())
    votey = votes_shelve[msg_id]  # Получаем необходимую нам голосовашку в хранилище
    file.close()

    if user_id in votey['votes'][which][1].keys(
    ):  # Челик нажал на кнопку, на которой есть его мнение
        # удаляем челика из словаря
        votey['votes'][which][1].pop(
            user_id)  # TODO Убрать быдлокод такого вида, изменив структуру МГ и АГ
    else:
        # если чедика нету - то просто добавляем
        votey['votes'][which][1].update([(user_id, link)])
    # Сохраняем изменения
    votes_shelve[msg_id] = votey
    file = open(MULTI_VOTES_FILE, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    answer_callback(call.id, text="Жмак учтён!")
    update_multi_vote(call.message.message_id)  # TODO возможность стопнуть мульти-голосовашку


def adapt_vote(call):
    """Обновляет адапт-голосовашку"""
    LOG.log_print("av invoked")
    user = call.from_user
    user_username = user.username  # юзернейм жмакнувшего челика
    user_nickname = user.first_name
    user_id = user.id
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    link = f'<a href="t.me/{user_username}">{user_nickname}</a>'
    which = int(call.data[-1])  # Где менять мнение
    file = open(ADAPT_VOTES_FILE, encoding='utf-8')
    votes_shelve = literal_eval(file.read())
    votey = votes_shelve[msg_id]  # Получаем необходимую нам голосовашку в хранилище
    file.close()
    if msg_id in votes_shelve.keys():
        if user_id in votey['votes'][which][1].keys(
        ):  # Челик нажал на кнопку, на которой есть его мнение
            # удаляем челика из словаря
            votey['votes'][which][1].pop(user_id)
        else:
            for i in votey['votes']:
                i[1].pop(user_id, None)
            # если чедика нету - то просто добавляем
            votey['votes'][which][1].update([(user_id, link)])
    # Сохраняем изменения
    votes_shelve[msg_id] = votey
    file = open(ADAPT_VOTES_FILE, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    answer_callback(call.id, text="Жмак учтён!")
    update_adapt_vote(call.message.message_id)  # TODO возможность стопнуть адапт-голосовашку


def add_vote(call):
    """Вставляет голос в голосоовашку"""
    LOG.log_print("add_vote invoked")
    reply_markup = VOTE_KEYBOARD
    text = ''
    user = call.from_user
    user_username = user.username  # юзернейм жмакнувшего челика
    user_nickname = user.first_name
    user_id = user.id
    msg_id = call.message.message_id  # Ай ди жмакнутого сообщения
    # Как этот челик будет отображаться в сообщении
    link = f'<a href="t.me/{user_username}">{user_nickname}</a>'
    file = open(VOTES_FILE, 'r', encoding='utf-8')
    votes_shelve = literal_eval(file.read())
    file.close()
    if msg_id in votes_shelve.keys():
        votey = votes_shelve[msg_id]  # Получаем необходимую нам голосовашку в хранилище
        if time() - votey['time'] > 86400 and len(votey['favor']) != len(
                votey['against']):  # это сутки
            reply_markup = None
            text += 'Голосование окончено. Новые голоса не принимаются\n\n'
        # Person clicked a button containing their opinion
        elif user_id in votey[call.data].keys():
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
        text += 'Голосование окончено по причине ненахода записи об этой голосовашки. ' \
                'Новые голоса не принимаются\n\n'
        text += call.message.text
    file = open(VOTES_FILE, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    edit_text(text=text,
              chat_id=call.message.chat.id,
              message_id=call.message.message_id,
              reply_markup=reply_markup,
              parse_mode="HTML")
    answer_callback(call.id, text="Жмак учтён!")


def vote(message):
    """Create poll"""
    LOG.log_print(f'vote invoked')
    where_keyboard = InlineKeyboardMarkup()
    where_keyboard.row_width = 1
    where_keyboard.add(InlineKeyboardButton("Сюда", callback_data="here"))
    reply(message, "А запостить куда?", reply_markup=where_keyboard)

# TODO разделить этот модуль на сообщения с кнопками и триггеры кнопок
