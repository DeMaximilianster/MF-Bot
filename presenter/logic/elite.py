from presenter.config.config_func import Database
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from view.output import send, register_handler, reply
from random import choice
from presenter.config.log import Loger, log_to
from random import shuffle

log = Loger(log_to)
elite_work = True


def ask_question(message, question):
    """Задаём вопрос"""
    log.log_print("ask_question invoked")
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


def submit(message):  # TODO возможность отменить свои ответы
    """Подсчитывает результаты"""
    log.log_print("submit invoked")
    database = Database()
    markup = ReplyKeyboardRemove(selective=False)  # убираем клаву
    success = 0  # Переменная для подсчёта правильных ответов
    person = message.from_user
    for i in range(1, 7):
        if database.get('basic_logic',
                        ('right', database.get('basic_logic_tested',
                                               ('id', message.from_user.id))[f'answer_{i}'])):
            success += 1
    # TODO записывать время прохождения
    # TODO В некоторые вопросы и ответы теста добавить капс лок
    # TODO Записывать результаты в elite_results
    if success >= 4:
        send(
            person.id,
            "Поздравляю! Количество ваших правильных ответов ({}) достаточно для прохождения".format(
                success),
            reply_markup=markup)
        send(
            -1001233124059, '#тест_на_логику {} ({}) [{}] осилил(а) тест со счётом {}'.format(
                person.first_name, person.username, person.id, success))
        # TODO вырубить повторные присылания сообщений о прохождении теста на логику
    else:
        send(person.id,
             "К сожалению, количество ваших правильных ответов ({}) недостаточно для прохождения".
             format(success),
             reply_markup=markup)
        send(
            -1001233124059, '#тест_на_логику {} ({}) [{}] провалил(а) тест со счётом {}'.format(
                person.first_name, person.username, person.id, success))


def check(message, ques):
    """Запись ответа"""
    log.log_print("check invoked")
    if message.text[0] == '/':
        reply(message,
              "Тест приостановлен, введите вашу команду ещё раз",
              reply_markup=ReplyKeyboardRemove(selective=False))
        return None
    database = Database()
    database.change(message.text, f'answer_{ques}', 'basic_logic_tested',
                    ('id', message.from_user.id))
    if ques != 6:
        ask_question(message, ques + 1)
    else:
        submit(message)


def elite(message):  # TODO Привести эти команды в порядок
    log.log_print("elite invoked")
    database = Database()
    if database.get('basic_logic_tested', ('id', message.from_user.id)) is None:
        send(
            message.chat.id,
            "Сейчас я буду давать вам утверждения, а вы выбирайте те, что из них логически вытекают")
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
        submit(message)  # TODO тест когда-то проходили, пересдача

# TODO Продвинутая логика
# TODO Сочинение
# TODO Мораль
