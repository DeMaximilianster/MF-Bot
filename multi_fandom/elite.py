from multi_fandom.config.config_var import *
from random import choice
elite_work = True


def shuffle(old_list):
    """Перемешивает список или кортеж"""
    old_list = list(old_list)
    new_list = []
    while old_list:
        element = choice(old_list)
        new_list.append(element)
        old_list.remove(element)
    return new_list


def ask_question(message, question):
    """Задаём вопрос"""
    database = Database()
    ask = database.get(message.from_user.id, 'basic_logic_tested')[question]  # Получаем вопрос
    note = database.get(ask, 'basic_logic', 'text')  # Получаем полную инфу о вопросе
    answers = note[2:]  # Получаем варианты ответов на вопрос
    answers = shuffle(answers)  # Перемешиваем ответы
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)  # Создаём клавиатуру для ответов
    for i in answers:  # Заполняем клавиатуру кнопками
        markup.add(i)
    sent = bot.send_message(message.from_user.id, note[1], reply_markup=markup)  # Отправляем сообщение
    del database
    bot.register_next_step_handler(sent, check)  # Следующее сообщение будет проверяться, как ответ на вопрос


def submit(message):  # TODO возможность отменить свои ответы
    """Подсчитывает результаты"""
    database = Database()
    markup = telebot.types.ReplyKeyboardRemove(selective=False)  # убираем клаву
    success = 0  # Переменная для подсчёта правильных ответов
    answers = database.get(message.from_user.id, 'basic_logic_tested')[7:13]
    person = message.from_user
    for i in range(6):
        if database.get(answers[i], 'basic_logic', 'right'):
            success += 1
    # TODO записывать время прохождения
    # TODO В некоторые вопросы и ответы теста добавить капс лок
    # TODO Записывать результаты в elite_results
    # TODO Добавить краткий єкскурс в тест на логику
    if success >= 4:
        bot.send_message(person.id, "Поздравляю! Количество ваших правильных ответов ({}) достаточно для прохождения"
                         .format(success), reply_markup=markup)
        bot.send_message(-1001233124059, '{} ({}) [{}] осилил(а) тест со счётом {}'
                         .format(person.first_name, person.username, person.id, success))
    else:
        bot.send_message(person.id, "К сожалению, количество ваших правильных ответов ({}) недостаточно для прохождения"
                         .format(success), reply_markup=markup)
        bot.send_message(-1001233124059, '{} ({}) [{}] провалил(а) тест со счётом {}'
                         .format(person.first_name, person.username, person.id, success))


def check(message):
    """Запись ответа"""
    database = Database()
    # TODO Пусть бот ставит тест на паузу, когда видит, что в сообщений есть "/"
    answer = 0
    person = database.get(message.from_user.id, 'basic_logic_tested')  # Запись чела в списке проходящих тест
    for i in range(7, 13):
        if person[i] == "None":
            answer = i - 6
            break
    database.change(message.text, message.from_user.id, 'basic_logic_tested', 'answer_{}'.format(answer))
    del database
    if answer != 6:
        elite(message)
    else:
        submit(message)


@bot.message_handler(commands=['elite'])  # TODO Привести эти команды в порядок
def elite(message):
    if message.chat.type != 'private':  # Тест на элитность можно провести только в личке у бота
        bot.reply_to(message, "Напиши мне это в личку, я в чате не буду этим заниматься")
        return None
    database = Database()
    print(database.get(message.from_user.id, table='basic_logic_tested'))
    if database.get(message.from_user.id, table='basic_logic_tested') is None:
        person = (message.from_user.id, 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None',
                  'None', 'None', 'None', 'None')
        database.append(person, 'basic_logic_tested')
        # Создаём список вопросов
        all_questions = list(range(1, 31))
        for i in range(6):
            question = choice(all_questions)
            value = database.get(question, 'basic_logic')[1]
            print(value)
            database.change(value, message.from_user.id, 'basic_logic_tested', 'question_{}'.format(i+1))
            all_questions.remove(question)
    print(database.get(message.from_user.id, 'basic_logic_tested'))
    print(database.get(message.from_user.id, 'basic_logic_tested')[7])
    for i in range(7, 13):
        if database.get(message.from_user.id, 'basic_logic_tested')[i] == "None":
            ask_question(message, i - 6)
            del database
            break
    else:
        submit(message)  # TODO тест когда-то проходили, пересдача
        del database
