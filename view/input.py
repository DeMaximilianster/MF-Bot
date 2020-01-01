from presenter.config.token import bot
from view.output import reply, answer_callback
from presenter.config.config_func import in_mf, cooldown, person_analyze, rank_required, rank_superiority, \
    appointment_required, int_check
from presenter.logic.elite import elite
from presenter.logic.boss_commands import ban, deleter_mode, give_admin, del_admin, set_guest, add_chat, warn, unwarn, \
    message_change, money_pay
from presenter.logic.complicated_commands import adequate, inadequate, response, insult, non_ironic, ironic, \
    place_here, mv, av, add_vote, vote
from presenter.logic.reactions import deleter, new_member, left_member
from presenter.logic.standart_commands import helper, send_drakken, send_me, send_meme, minet, show_id, \
    all_members, money_give, money_top, language_getter, month_set, day_set, birthday, admins, chat_check, \
    chats, anon_message
from presenter.logic.start import starter
from presenter.config.log import Loger, log_to
from requests import get

log = Loger(log_to)

'''Реакции на медиа, новых участников и выход участников'''


@bot.message_handler(content_types=['document', 'photo', 'sticker', 'video', 'video_note'])
def deleter_handler(message):
    """Удаляет медиа ночью"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None, or_private=False, loud=False):
        deleter(message)


@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    """Реагирует на вход в чат"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None, or_private=False):
        person = message.new_chat_members[0]
        if get(f"https://api.cas.chat/check?user_id={person.id}").json()["ok"]:
            # TODO Additional layer of anti-spam protection
            # TODO Deletion of spammer's messages and bots' greeting to it
            ban(message, person)
        else:
            new_member(message)


@bot.message_handler(content_types=['left_chat_member'])
def left_member_handler(message):
    """Комментирует уход участника и прощается участником"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None, or_private=False, loud=False):
        left_member(message)


'''Элитарные команды'''


@bot.message_handler(commands=['elite'])
def elite_handler(message):
    log.log_print(f"{__name__} invoked")
    if message.chat.type == 'private':  # Тест на элитность можно провести только в личке у бота
        elite(message)
    else:
        reply(message, "Напиши мне это в личку, я в чате не буду этим заниматься")


'''Админские обычные команды'''

"""
@bot.message_handler(commands=['search'])
def chat_search_handler(message):
    # Ищет чаты
    if in_mf(message) and rank_required(message, "Админ"):
        chat_search(message)
"""


@bot.message_handler(commands=['warn'])
def warn_handler(message):
    """Даёт участнику предупреждение"""
    log.log_print(f"{__name__} invoked")
    rep = message.reply_to_message
    if not rep:
        reply(message, "Надо ответить на сообщение с актом преступления, чтобы переслать контекст в хранилище")
    elif not int_check(message.text.split()[-1], positive=True) and len(message.text.split()) > 1:
        reply(message, "Последнее слово должно быть положительным числом, сколько варнов даём")
    elif in_mf(message, 'boss_commands', False) and appointment_required(message, "Admin") \
            and rank_superiority(message, rep.from_user):
        warn(message, rep.from_user.id)


@bot.message_handler(commands=['unwarn'])
def unwarn_handler(message):
    """Снимает с участника предупреждение"""
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message)
    if not int_check(message.text.split()[-1], positive=True) and len(message.text.split()) > 1:
        reply(message, "Последнее слово должно быть положительным числом, сколько варнов снимаем")
    elif in_mf(message, 'boss_commands', False) and appointment_required(message, "Admin") and person:
        unwarn(message, person)


@bot.message_handler(commands=['ban'])
def ban_handler(message):
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message)
    if in_mf(message, 'boss_commands', False) and appointment_required(message, "Admin") and person \
            and rank_superiority(message, person):
        ban(message, person)


@bot.message_handler(commands=['pay'])
def money_pay_handler(message):
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message, to_self=True)
    if not int_check(message.text.split()[-1], positive=False):
        reply(message, "Последнее слово должно быть числом, сколько ябломилианов прибавляем или убавляем")
    elif in_mf(message, 'financial_commands') and appointment_required(message, "Admin") and person:
        money_pay(message, person)


@bot.message_handler(commands=['delete_mode'])
def deleter_mode_handler(message):
    log.log_print(f"{__name__} invoked")
    if in_mf(message, 'boss_commands', False) and appointment_required(message, "Admin"):
        deleter_mode(message)


@bot.message_handler(commands=['admin'])
def give_admin_handler(message):
    """Назначает человека админом"""
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message)
    if in_mf(message, 'boss_commands') and rank_required(message, "The Committee Member") \
            and person and rank_superiority(message, person):
        give_admin(message, person)


@bot.message_handler(commands=['unadmin'])
def del_admin_handler(message):
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message)
    if in_mf(message, 'boss_commands') and rank_required(message, "The Committee Member") \
            and person and rank_superiority(message, person):
        del_admin(message, person)


@bot.message_handler(commands=['guest'])
def set_guest_handler(message):
    """Sets person's rank to guest"""
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message)
    if in_mf(message, 'boss_commands') and rank_required(message, "The Committee Member") \
            and person and rank_superiority(message, person):
        set_guest(message, person)


@bot.message_handler(commands=['messages'])
def messages_change_handler(message):
    """Меняет запись в БД о количестве сообщений чела"""
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message, to_self=True)
    if not int_check(message.text.split()[-1], positive=True):
        reply(message, "Последнее слово должно быть положительным числом, сколько сообщений ставим")
    elif in_mf(message, 'boss_commands', False) and appointment_required(message, "Admin") and person:
        if (len(message.text.split()) == 2 and message.reply_to_message) or len(message.text.split()) == 3:
            message_change(message, person)
        else:
            reply(message, "Либо не указана персона, к которой это применяется, либо количество сообщений")


@bot.message_handler(commands=['add_chat'])
def add_chat_handler(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    log.log_print(f"{__name__} invoked")
    if rank_required(message, "Deputy"):
        add_chat(message)


'''
@bot.message_handler(commands=['change_database'])
def database_changer_handler(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    log.log_print(f"{__name__} invoked")
    if rank_required(message, "Deputy"):
        database_changer()
'''

'''Составные команды'''


@bot.callback_query_handler(func=lambda call: 'adequate' in call.data and call.data != 'inadequate')
def adequate_handler(call):
    """Вариант адекватен"""
    log.log_print(f"{__name__} invoked")
    adequate(call)


@bot.callback_query_handler(func=lambda call: call.data == 'inadequate')
def inadequate_handler(call):
    """Вариант неадекватен"""
    log.log_print(f"{__name__} invoked")
    inadequate(call)


@bot.inline_handler(lambda query: query.query == 'test')
def response_handler(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    log.log_print(f"{__name__} invoked")
    response(inline_query)


@bot.message_handler(regexp='Признаю оскорблением')
def insult_handler(message):
    """Спращивает, иронично ли признание оскорблением"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, False):
        insult(message)


@bot.callback_query_handler(func=lambda call: call.data == 'non_ironic')  # триггерится, когда нажата кнопка "Нет"
def non_ironic_handler(call):
    """Реакция, если обвинение было неироничным"""
    log.log_print(f"{__name__} invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        non_ironic(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.callback_query_handler(func=lambda call: call.data == 'ironic')  # триггерится, когда нажата кнопка "Да"
def ironic_handler(call):
    """Реакция, если обвинение было ироничным"""
    log.log_print(f"{__name__} invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        ironic(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.message_handler(commands=['vote', 'multi_vote', 'adapt_vote'])
def vote_handler(message):
    """Генерирует голосовашку"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, 'standart_commands'):
        vote(message)


@bot.callback_query_handler(func=lambda call: 'here' in call.data or 'nedostream' in call.data)
def place_here_handler(call):
    """Выбирает, куда прислать голосовашку"""
    log.log_print(f"{__name__} invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        place_here(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.callback_query_handler(func=lambda call: 'mv_' in call.data)
def mv_handler(call):
    """Обновляет мульти-голосовашку"""
    log.log_print(f"{__name__} invoked")
    if call.chat_instance != "-8294084429973252853" or rank_required(call, "Citizen"):
        mv(call)


@bot.callback_query_handler(func=lambda call: 'av_' in call.data)
def av_handler(call):
    """Обновляет адапт-голосовашку"""
    log.log_print(f"{__name__} invoked")
    if call.chat_instance != "-8294084429973252853" or rank_required(call, "Citizen"):
        av(call)


@bot.callback_query_handler(func=lambda call: call.data == 'favor' or call.data == 'against' or call.data == 'abstain')
def add_vote_handler(call):
    """Вставляет голос в голосоовашку"""
    log.log_print(f"{__name__} invoked")
    if call.chat_instance != "-8294084429973252853" or rank_required(call, "Citizen"):
        add_vote(call)


'''Простые команды и старт'''


@bot.message_handler(commands=['lang'])
def language_getter_handler(message):
    """Gets the language of the chat"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None):
        language_getter(message)


@bot.message_handler(commands=['start'])
def starter_handler(message):
    """Запуск бота в личке, в чате просто реагирует"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None):
        starter(message)


@bot.message_handler(commands=['help'])
def helper_handler(message):
    """Предоставляет человеку список команд"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None):
        helper(message)


@bot.message_handler(commands=['id'])
def show_id_handler(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None):
        show_id(message)


@bot.message_handler(commands=['minet', 'french_style_sex', 'blowjob'])
def minet_handler(message):
    """Приносит удовольствие"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, 'standart_commands') and cooldown(message, 'minet'):
        minet(message)


@bot.message_handler(commands=['drakken'])
def send_drakken_handler(message):
    """Присылает арт с Доктором Драккеном"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, 'standart_commands') and cooldown(message, 'drakken'):
        send_drakken(message)


@bot.message_handler(regexp='есть один мем')
@bot.message_handler(commands=['meme'])
def send_meme_handler(message):
    """Присылает мем"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, 'standart_commands') and cooldown(message, 'meme'):
        send_meme(message)


@bot.message_handler(commands=['me', 'check', 'check_me', 'check_ebalo'])
def send_me_handler(message):
    """Присылает человеку его запись в БД"""
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message, to_self=True)
    if in_mf(message, command_type=None) and person:
        send_me(message, person)


@bot.message_handler(commands=['members', 'database'])
def all_members_handler(message):
    """Присылает человеку все записи в БД"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None):
        all_members(message)


@bot.message_handler(commands=['give'])
def money_give_handler(message):
    """Обмен денег между пользователями"""
    log.log_print(f"{__name__} invoked")
    person = person_analyze(message, to_bot=True)
    if not int_check(message.text.split()[-1], positive=False):
        reply(message, "Последнее слово должно быть числом, сколько денег даём")
    elif in_mf(message, 'financial_commands') and person:
        money_give(message, person)


@bot.message_handler(commands=['top'])
def money_top_handler(message):
    """Топ ЯМ"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, 'financial_commands'):
        money_top(message)


@bot.message_handler(commands=['month'])
def month_set_handler(message):
    """Set month of person's birthday"""
    log.log_print(f"{__name__} invoked")
    month = int_check(message.text.split()[-1], positive=True)
    if month is None:
        reply(message, "Последнее слово должно быть положительным числом -- номером месяца")
    elif not 1 <= month <= 12:
        reply(message, "Если ты вдруг не знаешь, то месяца имеют номера от 1 до 12")
    elif in_mf(message, command_type=None):
        month_set(message, month)


@bot.message_handler(commands=['day'])
def day_set_handler(message):
    """Set day of person's birthday"""
    log.log_print(f"{__name__} invoked")
    day = int_check(message.text.split()[-1], positive=True)
    if day is None:
        reply(message, "Последнее слово должно быть положительным числом -- номером дня")
    elif not 1 <= day <= 31:
        reply(message, "Если ты вдруг не знаешь, то дни имеют номера от 1 до 31")
    elif in_mf(message, command_type=None):
        day_set(message, day)


@bot.message_handler(commands=['bdays', 'birthdays'])
def birthday_handler(message):
    """Show the nearest birthdays"""
    log.log_print(f"{__name__} invoked")
    if in_mf(message, command_type=None):
        birthday(message)


@bot.message_handler(commands=['admins', 'report'])
def admins_handler(message):
    """Ping admins"""
    if in_mf(message, 'standart_commands') and rank_required(message, 'Citizen') and cooldown(message, 'admins', 300):
        admins(message)


@bot.message_handler(commands=['chat'])
def chat_check_handler(message):
    """Show options of the current chat"""
    if in_mf(message, command_type=None, or_private=False):
        chat_check(message)


@bot.message_handler(commands=['chats'])
def chats_handler(message):
    """Send chat list"""
    if in_mf(message, 'standart_commands'):
        chats(message)


@bot.message_handler(commands=['anon'])
def anon_message_handler(message):
    """Send anon message to admin place"""
    if message.chat.id > 0:
        if len(message.text) == 5:
            reply(message, "После команды /anon должно следовать то, что надо отправить админам")
        else:
            anon_message(message)
    else:
        reply(message, "И как это может быть анонимно?")


'''Последний хэндлер. Просто считает сообщения, что не попали в другие хэндлеры'''


@bot.message_handler(func=lambda message: True, content_types=None)
def counter_handler(message):
    """Подсчитывает сообщения"""
    log.log_print(f"{__name__} invoked")
    in_mf(message, command_type=None, loud=False)
