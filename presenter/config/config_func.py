# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from presenter.config.files_paths import adapt_votes_file, multi_votes_file, votes_file
from view.output import *
from presenter.config.log import Loger
from presenter.config.config_var import roles, bot_id
from presenter.config.log import log_to
from random import choice

log = Loger(log_to)


def language(message):
    languages = {"ru": False, "en": False}
    russian = set("ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ")
    english = set("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
    text = ""
    if message.chat.type == "private":
        user = message.from_user
        text += user.first_name
        if user.last_name:
            text += user.last_name
    else:
        chat = get_chat(message.chat.id)
        text += chat.title
        if chat.description:
            text += chat.description
    text = set(text)
    languages['ru'] = bool(russian & text) | (message.from_user.language_code == 'ru')
    languages['en'] = bool(english & text) | (message.from_user.language_code == 'en')
    return languages


def shuffle(old_list):
    """Перемешивает список или кортеж"""
    log.log_print("shuffle invoked")
    old_list = list(old_list)
    new_list = []
    while old_list:
        element = choice(old_list)
        new_list.append(element)
        old_list.remove(element)
    return new_list


def person_analyze(message, to_self=False, to_self_leader=False, to_bot=False):
    log.log_print("person_analyze invoked")
    if message.reply_to_message:  # Сообщение является ответом
        if message.reply_to_message.new_chat_members:
            person = message.reply_to_message.new_chat_members[0]
        else:
            person = message.reply_to_message.from_user
    elif len(message.text.split()) > 1:
        par = message.text.split()[1]
        if par.isdigit() and 7 <= len(par) <= 9:
            person = get_member(-1001408293838, par)
            if person:
                person = person.user
            else:
                reply(message, "Не вижу такого ID")
                return None
        else:
            reply(message, "Некорректный ID. ID это число, которое содержит в себе от 7 до 9 цифр")
            return None
    elif to_self:
        return message.from_user
    else:
        reply(message, "Ответьте на сообщение необходимого человека или напишите после команды его ID")
        return None
    if person.id == message.from_user.id and not to_self:
        if to_self_leader and rank_required(message, "Лидер", False):
            return person
        elif to_self_leader:
            reply(message, "Я вам запрещаю пользоваться этой командой на самом себе (если вы не Лидер, конечно)")
            return None
        else:
            reply(message, "Я вам запрещаю пользоваться этой командой на самом себе (даже если вы Лидер)")
            return None
    elif person.id == bot_id and not to_bot:
        reply(message, "Я вам запрещаю пользоваться этой командой на мне")
        return None
    else:
        return person


def rank_superiority(message):
    database = Database()
    your_rank = database.get(message.from_user.id)[3]
    their_rank = database.get(person_analyze(message).id)[3]
    del database
    your_rank_n = roles.index(your_rank)
    their_rank_n = roles.index(their_rank)
    if their_rank_n >= your_rank_n:
        reply(message, "Для этого ваше звание ({}) должно превосходить звание цели ({})".format(your_rank, their_rank))
        return False
    else:
        return True


def rank_required(message, min_rank, loud=True):
    log.log_print("rank_required invoked from userID {}".format(message.from_user.id))
    database = Database()
    your_rank = database.get(message.from_user.id)[3]
    your_rank_n = roles.index(your_rank)
    min_rank_n = roles.index(min_rank)
    if your_rank_n < min_rank_n and loud:
        reply(message, "Ваше звание ({}) не дотягивает до необходимого ({}) для данной команды"
                       .format(your_rank, min_rank))
    del database
    return your_rank_n >= min_rank_n


def cooldown(message):
    log.log_print("cooldown invoked")
    database = Database()
    # Получаем наименование необходимой команды
    if 'есть один мем' in message.text.lower():
        analyze = '/meme'
    else:
        analyze = message.text.split()[0]  # Первое слово в строке
        if '@' in analyze:
            analyze = analyze.split('@')[0]  # Убираем собачку и то, что после неё
    cooldown_id = '{} {}'.format(message.from_user.id, analyze)
    command = database.get(cooldown_id, 'cooldown')
    if not command:  # Чел впервые пользуется коммандой
        database.append((cooldown_id, message.date), 'cooldown')
        del database
        return True
    # Чел уже пользовался командой
    time_passed = message.date - command[1]
    if time_passed < 3600:  # Кулдаун не прошёл
        seconds = 3600 - time_passed
        minutes = seconds//60
        seconds %= 60
        answer = "Воу, придержи коней, ковбой. Ты сможешь воспользоваться этой командой только "
        answer += "через {} минут и {} секунд 🤠".format(minutes, seconds)
        reply(message, answer)
        del database
        return False
    else:  # Кулдаун прошёл
        database.change(message.date, cooldown_id, 'cooldown', 'time')
        del database
        return True


def time_replace(seconds):
    seconds += 3*60*60
    minutes = seconds//60
    seconds %= 60
    hours = minutes//60
    minutes %= 60
    days = hours//60
    hours %= 24
    return days, hours, minutes, seconds


def error(message, e):
    """Уведомляет Дэ'Максимилианстера об ошибке, не привёвшей к вылету"""
    send(381279599, "Произошла ошибка")
    send(381279599, e)
    reply(message, "У меня произошла непроизвольная дефекация")
    print(e)


def in_mf(message, lang, or_private=True):
    """Позволяет регулировать использование команл вне чатов и в личке"""
    log.log_print("in_mf invoked")
    database = Database()
    if database.get(message.chat.id, 'chats'):  # Команда вызвана в системе МФ2
        counter(message)  # Отправляем сообщение на учёт в БД
        return True
    elif message.chat.type == 'private':  # Команда вызвана в личке
        if or_private:  # Команда одобрена для использования в личке (например /minet)
            return True
        else:  # Команда не одобрена для использования в личке (например /ban)
            person = message.from_user
            send(381279599, "Некто {} ({}) [{}] попыталcя использовать команду {} в личке"
                            .format(person.first_name, person.username, person.id, message.text))
            reply(message, "Эта команда отключена в ЛС")
            return False
    text = "Жалкие завистники из чата с ID {} и названием {}, в частности {} (@{}) [{}] попытались мной воспользоваться"
    send(381279599, text.format(message.chat.id, message.chat.title, message.from_user.first_name,
                                message.from_user.username, message.from_user.id))
    rep_text = ""
    if lang['en']:
        rep_text += "I don't work here. But I work in @MultiFandomEn\n\n"
    if lang['ru']:
        rep_text += "Я тут не работаю. Зато я работаю в @MultiFandomRu\n\n"
    reply(message, rep_text)
    return False


def counter(message):
    """Подсчитывает сообщения, отправленные челом"""
    log.log_print("counter invoked")
    database = Database()
    if message.new_chat_members:
        person = message.new_chat_members[0]
    else:
        person = message.from_user
    if database.get(person.id) is None:  # Нет такой записи
        answer = 'Добро пожаловать в наш чат! Напиши мне в личку и в будущем получишь доступ '
        answer += 'к различным функциям. Читай закреп, веди себя хорошо, приятного времяпровождения!'
        reply(message, answer)
        try:
            person = (person.id, str(person.username), person.first_name, 'Гость', 1, 0, 0)
            database.append(person)
        except Exception as e:
            error(message, e)
    elif message.chat.id in [x[0] for x in database.get_many('Главный чат') + database.get_many('Подчат')]:
        value = database.get(person.id)[4] + 1
        database.change(value, person.id, 'members', 'messages', 'id')
        # TODO Добавить время последнего сообщения и элитократические взаимодействия с ним
    del database


# TODO перенести все голосовашки в базу данных или ещё куда-то (JSON)
def create_vote(vote_message):
    """Создаёт голосовашку"""
    log.log_print("create_vote invoked")
    # TODO Параметр purpose, отвечающий за действие, которое надо сделать при закрытии голосовашки
    file = open(votes_file, 'r', encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"time": vote_message.date, "text": vote_message.text,
                                             "favor": {}, "against": {}, "abstain": {}}
    file = open(votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()


def create_multi_vote(vote_message):
    """Создаёт мульти-голосовашку"""
    log.log_print("create_multi_vote invoked")
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    file = open(multi_votes_file, encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"text": vote_message.text, "votes": [], "keyboard": [],
                                             "chat": vote_message.chat.id}
    file = open(multi_votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


def create_adapt_vote(vote_message):
    """Создаёт адапт-голосовашку"""
    log.log_print("create_adapt_vote invoked")
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_adapt_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    file = open(adapt_votes_file, encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"text": vote_message.text, "votes": [], "keyboard": [],
                                             "chat": vote_message.chat.id}
    file = open(adapt_votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


def update_multi_vote(vote_id):
    """Обновляет мульти-голосовашку"""
    log.log_print("update_multi_vote invoked")
    file = open(multi_votes_file, encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votey = dict(votes_shelve[vote_id])
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_option{}'.format(vote_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    for i in votey['keyboard']:
        keyboard.add(InlineKeyboardButton(i, callback_data='mv_'+str(votey['keyboard'].index(i))))
    # Меняем текст голосовашки
    text = votey["text"]
    for i in votey['votes']:
        text += '\n{}: '.format(i[0]) + ', '.join(i[1].values())
    try:
        edit_text(text=text, chat_id=votey['chat'], message_id=vote_id, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        print(e)


def update_adapt_vote(vote_id):
    """Обновляет адапт голосовашку"""
    log.log_print("update_adapt_vote")
    file = open(adapt_votes_file, encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votey = dict(votes_shelve[vote_id])
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_adapt_option{}'.format(vote_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    for i in votey['keyboard']:
        keyboard.add(InlineKeyboardButton(i, callback_data='av_'+str(votey['keyboard'].index(i))))
    # Меняем текст голосовашки
    text = votey["text"]
    for i in votey['votes']:
        text += '\n{}: '.format(i[0]) + ', '.join(i[1].values())
    try:
        edit_text(text=text, chat_id=votey['chat'], message_id=vote_id, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        print(e)
