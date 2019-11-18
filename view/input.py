from presenter.config.token import bot
from view.output import reply, answer_callback
from presenter.config.config_func import in_mf, counter, cooldown, person_analyze, rank_required, rank_superiority
from presenter.logic.elite import elite
from presenter.logic.boss_commands import ban, deleter_mode, promotion, demotion, add_chat, warn, unwarn,\
    message_change, money_pay
from presenter.logic.complicated_commands import adequate, inadequate, response, insult, non_ironic, ironic, \
    vote, place_here, mv, av, add_vote
from presenter.logic.reactions import deleter, new_member, left_member
from presenter.logic.standart_commands import helper, send_drakken, send_me, send_meme, minet, show_id, \
    all_members, money_give, money_top
from presenter.logic.start import starter
from presenter.config.log import Loger, log_to

log = Loger(log_to)


'''Реакции на медиа, новых участников и выход участников'''


@bot.message_handler(content_types=['document', 'photo', 'sticker', 'video', 'video_note'])
def deleter_handler(message):
    """Удаляет медиа ночью"""
    log.log_print("night media invoked")
    if in_mf(message):  # Если в МФ2 - то удаляем
        deleter(message)


@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    """Реагирует на вход в чат"""
    if in_mf(message):
        new_member(message)


@bot.message_handler(content_types=['left_chat_member'])
def left_member_handler(message):
    """Комментирует уход участника и прощается участником"""
    if in_mf(message):
        left_member(message)


'''Элитарные команды'''


@bot.message_handler(commands=['elite'])
def elite_handler(message):
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
    if in_mf(message, False) and rank_required(message, "Админ") and person_analyze(message)\
            and rank_superiority(message):
        if message.reply_to_message:
            warn(message)
        else:
            reply(message, "Надо ответить на сообщение с актом преступления, чтобы переслать контекст в хранилище")


@bot.message_handler(commands=['unwarn'])
def unwarn_handler(message):
    """Снимает с участника предупреждение"""
    if in_mf(message, False) and rank_required(message, "Админ") and person_analyze(message):
        unwarn(message)


@bot.message_handler(commands=['ban'])
def ban_handler(message):
    if in_mf(message, False) and rank_required(message, "Админ") and person_analyze(message)\
            and rank_superiority(message):
        ban(message)


@bot.message_handler(commands=['pay'])
def money_pay_handler(message):
    if in_mf(message, False) and rank_required(message, "Админ") and person_analyze(message):
        money_pay(message)


@bot.message_handler(commands=['delete_mode'])
def deleter_mode_handler(message):
    if in_mf(message, False) and rank_required(message, "Админ"):
        deleter_mode(message)


@bot.message_handler(commands=['admin'])
def promotion_handler(message):
    """Назначает человека админом"""
    if in_mf(message, False) and rank_required(message, "Член Комитета") and person_analyze(message)\
            and rank_superiority(message):
        promotion(message)


@bot.message_handler(commands=['guest'])
def demotion_handler(message):
    """Забирает у человека админку"""
    if in_mf(message, False) and rank_required(message, "Член Комитета") and person_analyze(message)\
            and rank_superiority(message):
        demotion(message)


@bot.message_handler(commands=['messages'])
def messages_change_handler(message):
    """Меняет запись в БД о количестве сообщений чела"""
    if in_mf(message, False) and rank_required(message, "Член Комитета") and person_analyze(message):
        if (len(message.text.split()) == 2 and message.reply_to_message) or len(message.text.split()) == 3:
            message_change(message)
        else:
            reply(message, "Либо не указана персона, к которой это применяется, либо количество сообщений")


@bot.message_handler(commands=['add_chat'])
def add_chat_handler(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    if rank_required(message, "Заместитель"):
        add_chat(message)


'''Составные команды'''


@bot.callback_query_handler(func=lambda call: 'adequate' in call.data and call.data != 'inadequate')
def adequate_handler(call):
    """Вариант адекватен"""
    adequate(call)


@bot.callback_query_handler(func=lambda call: call.data == 'inadequate')
def inadequate_handler(call):
    """Вариант неадекватен"""
    inadequate(call)


@bot.inline_handler(lambda query: query.query == 'test')
def response_handler(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    response(inline_query)


@bot.message_handler(regexp='Признаю оскорблением')
def insult_handler(message):
    """Спращивает, иронично ли признание оскорблением"""
    if in_mf(message, False):
        insult(message)


@bot.callback_query_handler(func=lambda call: call.data == 'non_ironic')  # триггерится, когда нажата кнопка "Нет"
def non_ironic_handler(call):
    """Реакция, если обвинение было неироничным"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        non_ironic(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.callback_query_handler(func=lambda call: call.data == 'ironic')  # триггерится, когда нажата кнопка "Да"
def ironic_handler(call):
    """Реакция, если обвинение было ироничным"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        ironic(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.message_handler(commands=['vote', 'multi_vote', 'adapt_vote'])
def vote_handler(message):
    """Генерирует голосовашку"""
    if in_mf(message, False) and rank_required(message, "Админ"):
        vote(message)


@bot.callback_query_handler(func=lambda call: 'here' in call.data)
def place_here_handler(call):
    """Выбирает, куда прислать голосовашку"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        place_here(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.callback_query_handler(func=lambda call: 'mv_' in call.data)
def mv_handler(call):
    """Обновляет мульти-голосовашку"""
    mv(call)


@bot.callback_query_handler(func=lambda call: 'av_' in call.data)
def av_handler(call):
    """Обновляет адапт-голосовашку"""
    av(call)


@bot.callback_query_handler(func=lambda call: call.data == 'favor' or call.data == 'against' or call.data == 'abstain')
def add_vote_handler(call):
    """Вставляет голос в голосоовашку"""
    add_vote(call)


'''Простые команды и старт'''


@bot.message_handler(commands=['start'])
def starter_handler(message):
    """Запуск бота в личке, в чате просто реагирует"""
    if in_mf(message):
        starter(message)


@bot.message_handler(commands=['help'])
def helper_handler(message):
    """Предоставляет человеку список команд"""
    if in_mf(message):
        helper(message)


@bot.message_handler(commands=['id'])
def show_id_handler(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    if in_mf(message):
        show_id(message)


@bot.message_handler(commands=['minet'])
def minet_handler(message):
    """Приносит удовольствие"""
    if in_mf(message) and cooldown(message):
        minet(message)


@bot.message_handler(commands=['drakken'])
def send_drakken_handler(message):
    """Присылает арт с Доктором Драккеном"""
    if in_mf(message) and cooldown(message):
        send_drakken(message)


@bot.message_handler(regexp='есть один мем')
@bot.message_handler(commands=['meme'])
def send_meme_handler(message):
    """Присылает мем"""
    if in_mf(message) and cooldown(message):
        send_meme(message)


@bot.message_handler(commands=['me', 'check', 'check_me', 'check_ebalo'])
def send_me_handler(message):
    """Присылает человеку его запись в БД"""
    if in_mf(message):
        send_me(message)


@bot.message_handler(commands=['members', 'database'])
def all_members_handler(message):
    """Присылает человеку все записи в БД"""
    if in_mf(message):
        all_members(message)


@bot.message_handler(commands=['give'])
def money_give_handler(message):
    """Обмен денег между пользователями"""
    if in_mf(message) and person_analyze(message, to_bot=True):
        money_give(message)


@bot.message_handler(commands=['top'])
def money_top_handler(message):
    """Топ ЯМ"""
    if in_mf(message):
        money_top(message)


'''Последний хэндлер. Просто считает сообщения, что не попали в другие хэндлеры'''


@bot.message_handler(func=lambda message: True, content_types=None)
def counter_handler(message):
    """Подсчитывает сообщения"""
    counter(message)
