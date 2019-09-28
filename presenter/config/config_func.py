# -*- coding: utf-8 -*-
from presenter.config.database_lib import Database
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from presenter.config.files_paths import adapt_votes_file, multi_votes_file, votes_file
from view.output import *
from presenter.config.log import Loger, LOG_TO_CONSOLE
from presenter.config.config_var import superior_roles, admin_roles

log = Loger(LOG_TO_CONSOLE)


def person_analyze(message, to_self=False):
    if message.reply_to_message:  # Сообщение является ответом
        return message.reply_to_message.from_user
    elif len(message.text.split()) > 1:
        par = message.text.split()[1]
        try:
            if int(par) and len(str(par)) == 9:
                return get_member(-1001408293838, par).user
            else:
                reply(message, "Некорректный ID. ID содержит в себе 9 цифр")
                return None
        except Exception as e:
            print(e)
            reply(message, "Некорректный ID. ID это целое число. Либо такого ID ни у кого нет")
            return None
    elif to_self:
        return message.from_user
    else:
        reply(message, "Ответьте на сообщение необходимого человека или напишите после команды его ID")
        return None


def is_admin(message, superior=False):
    log.log_print("Проверяем пользователя {0} на админку".format(message.from_user.username))
    database = Database()
    rank = database.get(message.from_user.id)[3]  # Получаем его звание
    del database
    if superior:  # Обязательно быть Лидером или Заместителем
        if rank in superior_roles:
            return True
        else:
            reply(message, "Э, нет, эта кнопка только для Лидера и его Заместителя")
            return False
    elif rank in admin_roles:
        return True
    else:
        reply(message, "Э, нет, эта кнопка только для админов")
        return False


def cooldown(message):
    log.log_print("Вызвана функция cooldown с параметрами {}:{}".format(message.from_user.id, message.text))
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
    if time_passed < 60:  # Кулдаун не прошёл
        answer = "Воу, придержи коней, ковбой. Ты сможешь воспользоваться этой командой только "
        answer += "через {} секунд 🤠".format(60 - time_passed)
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


def in_mf(message, or_private=True):
    """Позволяет регулировать использование команл вне чатов и в личке"""
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
    reply(message, "Я тут не работаю. Зато я работаю в @MultiFandomRu")
    return False


def counter(message):
    """Подсчитывает сообщения, отправленные челом"""
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
    elif message.chat.id == database.get('Главный чат', 'chats', 'purpose')[0]:  # Сообщение в главном чате
        value = database.get(person.id)[4] + 1
        database.change(value, person.id, 'members', 'messages', 'id')
    del database


# TODO перенести все голосовашки в базу данных или ещё куда-то (JSON)
def create_vote(vote_message):
    """Создаёт голосовашку"""
    log.log_print("Создаём голосовашку с текстом: "+vote_message.text)
    # TODO Параметр purpose, отвечающий за действие, которое надо сделать при закрытии голосовашки
    file = open(votes_file, 'r')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"time": vote_message.date, "text": vote_message.text,
                                             "favor": {}, "against": {}, "abstain": {}}
    file = open(votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()


def create_multi_vote(vote_message):
    """Создаёт мульти-голосовашку"""
    log.log_print("Создаём мульти-голосовашку с текстом: "+vote_message.text)
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    file = open(multi_votes_file)
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"text": vote_message.text, "votes": [], "keyboard": [],
                                             "chat": vote_message.chat.id}
    file = open(multi_votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


def create_adapt_vote(vote_message):
    """Создаёт адапт-голосовашку"""
    log.log_print("Создаём адапт-голосовашку с текстом: "+vote_message.text)
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_adapt_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    file = open(adapt_votes_file)
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"text": vote_message.text, "votes": [], "keyboard": [],
                                             "chat": vote_message.chat.id}
    file = open(adapt_votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


def update_multi_vote(vote_id):
    """Обновляет мульти-голосовашку"""
    log.log_print("обновляем мульти-голосовашку с id: "+str(vote_id))
    file = open(multi_votes_file)
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
    log.log_print("обновляем адапт-голосовашку с id: "+str(vote_id))
    file = open(adapt_votes_file)
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



