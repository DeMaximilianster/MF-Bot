"""Module for elite testing"""

from random import shuffle, choice
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from presenter.config.config_func import Database
from presenter.config.log import Logger, LOG_TO
from view.output import send, register_handler, reply


LOG = Logger(LOG_TO)


@LOG.wrap
def ask_question(message, question):
    """Задаём вопрос"""
    database = Database()
    ask = database.get('basic_logic_tested',
                       ('id', message.from_user.id))[f'question_{question}']  # Получаем вопрос
    note = database.get('basic_logic', ('text', ask))  # Получаем полную инфу о вопросе
    # Получаем варианты ответов на вопрос
    answers = [note['right'], note['wrong_1'], note['wrong_2']]
    shuffle(answers)  # Перемешиваем ответы
    markup = ReplyKeyboardMarkup(row_width=3)  # Создаём клавиатуру для ответов
    for i in answers:  # Заполняем клавиатуру кнопками
        markup.add(i)
    sent = send(message.from_user.id, note['text'], reply_markup=markup)  # Отправляем сообщение
    register_handler(sent, check,
                     question)  # Следующее сообщение будет проверяться, как ответ на вопрос


@LOG.wrap
def submit(message):
    """Подсчитывает результаты"""
    database = Database()
    markup = ReplyKeyboardRemove(selective=False)  # убираем клаву
    success = 0  # Переменная для подсчёта правильных ответов
    person = message.from_user
    for i in range(1, 7):
        if database.get('basic_logic',
                        ('right', database.get('basic_logic_tested',
                                               ('id', message.from_user.id))[f'answer_{i}'])):
            success += 1
    if success >= 4:
        send(person.id,
             "Поздравляю! Ваше количество баллов ({}) достаточно для прохождения".format(
                 success),
             reply_markup=markup)
        send(
            -1001233124059, '#тест_на_логику {} ({}) [{}] осилил(а) тест со счётом {}'.format(
                person.first_name, person.username, person.id, success))
    else:
        send(person.id,
             "К сожалению, количество ваших правильных ответов ({}) недостаточно для прохождения".
             format(success),
             reply_markup=markup)
        send(
            -1001233124059, '#тест_на_логику {} ({}) [{}] провалил(а) тест со счётом {}'.format(
                person.first_name, person.username, person.id, success))


@LOG.wrap
def check(message, ques):
    """Запись ответа"""
    if message.text[0] == '/':
        reply(message,
              "Тест приостановлен, введите вашу команду ещё раз",
              reply_markup=ReplyKeyboardRemove(selective=False))
    else:
        database = Database()
        database.change(message.text, f'answer_{ques}', 'basic_logic_tested',
                        ('id', message.from_user.id))
        if ques != 6:
            ask_question(message, ques + 1)
        else:
            submit(message)


@LOG.wrap
def elite(message):
    """Start the basic logic test"""
    database = Database()
    if database.get('basic_logic_tested', ('id', message.from_user.id)) is None:
        send(
            message.chat.id,
            "Сейчас я буду давать вам утверждения. Выбирайте те, что из них логически вытекают")
        person = (message.from_user.id, 'None', 'None', 'None', 'None', 'None', 'None', 'None',
                  'None', 'None', 'None', 'None', 'None', 'None')
        database.append(person, 'basic_logic_tested')
        # Создаём список вопросов
        all_questions = list(range(1, 31))
        for i in range(6):
            question = choice(all_questions)
            value = database.get('basic_logic', ('id', question))['text']
            print(value)
            database.change(value, f'question_{i + 1}', 'basic_logic_tested',
                            ('id', message.from_user.id))
            all_questions.remove(question)
    for i in range(1, 7):
        if database.get('basic_logic_tested', ('id', message.from_user.id))[
                f'answer_{i}'] == "None":
            ask_question(message, i)

            break
    else:
        submit(message)
