from presenter.config.config_func import Database, shuffle
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from view.output import send, register_handler
from random import choice
from presenter.config.log import Loger, log_to

log = Loger(log_to)
elite_work = True


def ask_question(message, question):
    """Задаём вопрос"""
    log.log_print("ask_question invoked")
    database = Database()
    ask = database.get('basic_logic_tested', ('id', message.from_user.id))[question]  # Получаем вопрос
    note = database.get('basic_logic', ('text', ask))  # Получаем полную инфу о вопросе
    answers = note[2:]  # Получаем варианты ответов на вопрос
    answers = shuffle(answers)  # Перемешиваем ответы
    markup = ReplyKeyboardMarkup(row_width=3)  # Создаём клавиатуру для ответов
    for i in answers:  # Заполняем клавиатуру кнопками
        markup.add(i)
    sent = send(message.from_user.id, note[1], reply_markup=markup)  # Отправляем сообщение
    register_handler(sent, check, question)  # Следующее сообщение будет проверяться, как ответ на вопрос


def submit(message):  # TODO возможность отменить свои ответы
    """Подсчитывает результаты"""
    log.log_print("submit invoked")
    database = Database()
    markup = ReplyKeyboardRemove(selective=False)  # убираем клаву
    success = 0  # Переменная для подсчёта правильных ответов
    answers = database.get('basic_logic_tested', ('id', message.from_user.id))[7:13]
    person = message.from_user
    for i in range(6):
        if database.get('basic_logic', ('right', answers[i])):
            success += 1
    # TODO записывать время прохождения
    # TODO В некоторые вопросы и ответы теста добавить капс лок
    # TODO Записывать результаты в elite_results
    if success >= 4:
        send(person.id, "Поздравляю! Количество ваших правильных ответов ({}) достаточно для прохождения"
                        .format(success), reply_markup=markup)
        send(-1001233124059, '#тест_на_логику {} ({}) [{}] осилил(а) тест со счётом {}'
                             .format(person.first_name, person.username, person.id, success))
    else:
        send(person.id, "К сожалению, количество ваших правильных ответов ({}) недостаточно для прохождения"
                        .format(success), reply_markup=markup)
        send(-1001233124059, '#тест_на_логику {} ({}) [{}] провалил(а) тест со счётом {}'
                             .format(person.first_name, person.username, person.id, success))


def check(message, ques):
    """Запись ответа"""
    log.log_print("check invoked")
    database = Database()
    # TODO Пусть бот ставит тест на паузу, когда видит, что в сообщений есть "/"
    person = database.get('basic_logic_tested', ('id', message.from_user.id))  # Запись чела в списке проходящих тест
    database.change(message.text, f'answer_{ques}', 'basic_logic_tested', ('id', message.from_user.id))
    if ques != 6:
        ask_question(message, ques+1)
    else:
        submit(message)


def elite(message):  # TODO Привести эти команды в порядок
    log.log_print("elite invoked")
    database = Database()
    if database.get('basic_logic_tested', ('id', message.from_user.id)) is None:
        send(message.chat.id, "Сейчас я буду давать вам утверждения, а вы выбирайте те, что из них логически вытекают")
        person = (message.from_user.id, 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None',
                  'None', 'None', 'None', 'None')
        database.append(person, 'basic_logic_tested')
        # Создаём список вопросов
        all_questions = list(range(1, 31))
        for i in range(6):
            question = choice(all_questions)
            value = database.get('basic_logic', ('id', question))[1]
            print(value)
            database.change(value, f'question_{i+1}', 'basic_logic_tested', ('id', message.from_user.id))
            all_questions.remove(question)
    for i in range(7, 13):
        if database.get('basic_logic_tested', ('id', message.from_user.id))[i] == "None":
            ask_question(message, i - 6)
            del database
            break
    else:
        submit(message)  # TODO тест когда-то проходили, пересдача
        del database


# TODO Продвинутая логика
# TODO Сочинение
# TODO Мораль
