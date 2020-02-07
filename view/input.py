from presenter.config.token import bot
from view.output import reply, answer_callback, send_document
from presenter.config.config_func import in_mf, cooldown, person_analyze, rank_superiority, \
     int_check, person_check, is_suitable, in_system_commands, is_correct_message, remove_slash_and_bot_mention, \
     convert_command_to_storage_content
from presenter.logic.elite import elite
from presenter.logic.boss_commands import ban, add_chat, add_admin_place, chat_options, system_options, \
    warn, unwarn, message_change, money_pay, rank_changer, mute, money_mode_change, money_emoji, money_name, \
    update_all_members, add_stuff_to_storage
from presenter.logic.complicated_commands import adequate, inadequate, response, insult, non_ironic, ironic, \
    place_here, mv, av, add_vote, vote, captcha_completed, captcha_failed
import presenter.logic.reactions as reactions
from presenter.logic.standart_commands import helper, send_me, send_meme, minet, \
    money_give, language_getter, month_set, day_set, birthday, admins, chat_check, \
    anon_message, system_check, money_helper, send_stuff_from_storage, send_some_top
from presenter.logic.start import starter
from presenter.config.log import Loger, log_to
from presenter.config.config_var import features_defaulters, features_oners, features_offers, system_features_offers, \
    system_features_oners, porn_adders, stuff_adders, all_content_types, commands_to_add_stuff,\
    commands_to_add_vulgar_stuff
from presenter.config.files_paths import votes_file, database_file, adapt_votes_file, multi_votes_file,  systems_file, \
    storage_file
import presenter.logic.developer_commands as developer_commands

# TODO Убрать этот ебучий срач
log = Loger(log_to)
trash = []
new_dudes = {}


'''Реакции на медиа, новых участников и выход участников'''


@bot.message_handler(content_types=['migrate_from_chat_id'])
def chat_id_update_handler(message):
    log.log_print("chat_id_update_handler invoked")
    reactions.chat_id_update(message)


@bot.message_handler(content_types=['document', 'photo', 'sticker', 'video', 'video_note'])
def deleter_handler(message):
    """Удаляет медиа ночью"""
    log.log_print(f"deleter_handler invoked")
    global new_dudes
    if in_mf(message, command_type=None, or_private=False, loud=False):
        reactions.deleter(message)


@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    """Реагирует на вход в чат"""
    log.log_print("new_member_handler invoked")
    global new_dudes
    person = message.new_chat_members[0]
    if in_mf(message, command_type=None, or_private=False):
        reactions.new_member(message, person)


@bot.message_handler(content_types=['left_chat_member'])
def left_member_handler(message):
    """Комментирует уход участника и прощается участником"""
    log.log_print("left_member_handler invoked")
    if in_mf(message, command_type=None, or_private=False, loud=False):
        reactions.left_member(message)


'''Элитарные команды'''


@bot.message_handler(commands=['elite'])
def elite_handler(message):
    log.log_print("elite_handler invoked")
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


@bot.message_handler(commands=commands_to_add_vulgar_stuff)
def upload_vulgar_stuff_to_storage_handler(message):
    log.log_print("upload_vulgar_stuff_to_storage_handler invoked")
    command = convert_command_to_storage_content(message.text)
    if in_mf(message, 'erotic_commands'):
        if message.from_user.id in porn_adders:
            add_stuff_to_storage(message, command)
        else:
            reply(message, "Не-а, вы не числитесь в рядах добавлятелей 'контента'")


@bot.message_handler(commands=commands_to_add_stuff)
def upload_stuff_to_storage_handler(message):
    log.log_print("upload_stuff_to_storage_handler invoked")
    command = convert_command_to_storage_content(message.text)
    if in_mf(message, command_type=None):
        if message.from_user.id in stuff_adders:
            add_stuff_to_storage(message, command)
        else:
            reply(message, "Не-а, вы не числитесь в рядах добавлятелей контента")


@bot.message_handler(commands=['update'])
def update_all_members_handler(message):
    log.log_print("update_all_members_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user, 'boss'):
        update_all_members(message)


@bot.message_handler(commands=['warn'])
def warn_handler(message):
    """Даёт участнику предупреждение"""
    log.log_print("warn_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user, 'boss'):
        rep = message.reply_to_message
        if rep:
            if person_check(message, rep.from_user) and rank_superiority(message, rep.from_user):
                if int_check(message.text.split()[-1], positive=True) or len(message.text.split()) == 1:
                    warn(message, rep.from_user)
                else:
                    reply(message, "Последнее слово должно быть положительным числом, сколько варнов даём")
        else:
            reply(message, "Надо ответить на сообщение с актом преступления, чтобы переслать контекст в хранилище")


@bot.message_handler(commands=['unwarn'])
def unwarn_handler(message):
    """Снимает с участника предупреждение"""
    log.log_print("unwarn_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user, 'boss'):
        person = person_analyze(message, to_bot=True)
        if person:
            if int_check(message.text.split()[-1], positive=True) or len(message.text.split()) == 1:
                unwarn(message, person)
            else:
                reply(message, "Последнее слово должно быть положительным числом, сколько варнов снимаем")


@bot.message_handler(commands=['ban'])
def ban_handler(message):
    log.log_print(f"ban_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user, 'boss'):
        person = person_analyze(message)
        if person and rank_superiority(message, person):
            ban(message, person)


@bot.message_handler(commands=['kick'])
def kick_handler(message):
    log.log_print(f"kick_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user, 'boss'):
        person = person_analyze(message)
        if person and rank_superiority(message, person):
            ban(message, person, unban_then=True)


@bot.message_handler(commands=['mute'])
def mute_handler(message):
    log.log_print("mute_handler invoked")
    if in_mf(message, "boss_commands", or_private=False) and is_suitable(message, message.from_user, 'boss'):
        person = person_analyze(message)
        if person and rank_superiority(message, person):
            if int_check(message.text.split()[-1], positive=True):  # TODO Добавить час мута по умолчанию
                mute(message, person)
            else:
                reply(message, "Последнее слово должно быть положительным числом на сколько часов запрещаем писать")


@bot.message_handler(commands=['pay'])
def money_pay_handler(message):
    log.log_print(f"money_pay_handler invoked")
    if in_mf(message, 'financial_commands', or_private=False) and is_suitable(message, message.from_user, 'boss'):
        person = person_analyze(message, to_self=True)
        if person:
            if int_check(message.text.split()[-1], positive=False):
                money_pay(message, person)
            else:
                reply(message, "Последнее слово должно быть числом, сколько валюты прибавляем или убавляем")


'''
@bot.message_handler(commands=['delete_mode'])
def deleter_mode_handler(message):
    log.log_print(f"{__name__} invoked")
    if in_mf(message, 'boss_commands', False) and is_suitable(message, message.from_user, "boss"):
        deleter_mode(message)
'''


@bot.message_handler(func=lambda message: in_system_commands(message))
def rank_changer_handler(message):
    """Sets person's rank to guest"""
    log.log_print("rank_changer_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        if message.from_user.id == 381279599:  # TODO Сделать так, чтоб добавлять можно было только лидера
            person = person_analyze(message)
            if person:
                rank_changer(message, person)
        elif is_suitable(message, message.from_user, 'boss'):
            person = person_analyze(message)
            if person and rank_superiority(message, person):
                rank_changer(message, person)


@bot.message_handler(commands=['messages'])
def messages_change_handler(message):
    """Меняет запись в БД о количестве сообщений чела"""
    log.log_print(f"messages_change_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user, "boss"):
        if (len(message.text.split()) == 2 and message.reply_to_message) or len(message.text.split()) == 3:
            person = person_analyze(message, to_self=True)
            if person:
                if int_check(message.text.split()[-1], positive=True):
                    message_change(message, person)
                else:
                    reply(message, "Последнее слово должно быть положительным числом, сколько сообщений ставим")
        else:
            reply(message, "Либо не указана персона, к которой это применяется, либо количество сообщений")


@bot.message_handler(commands=['add_chat'])
def add_chat_handler(message):  # TODO Она работает в личке, а не должна
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    log.log_print(f"add_chat_handler invoked")
    add_chat(message)


@bot.message_handler(commands=['admin_place'])
def add_admin_place_handler(message):
    """Add admin place to system"""
    log.log_print("add_admin_place_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message, message.from_user, "chat_changer"):
        add_admin_place(message)


@bot.message_handler(commands=['money_on', 'money_off'])
def money_mode_change_handler(message):
    log.log_print("money_mode_change_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message, message.from_user, "chat_changer"):
        money_mode_change(message)


@bot.message_handler(commands=['m_emoji'])
def money_emoji_handler(message):
    log.log_print("money_emoji_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message, message.from_user, "chat_changer"):
        money_emoji(message)


@bot.message_handler(commands=['m_name'])
def money_name_handler(message):
    log.log_print("money_name_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message, message.from_user, "chat_changer"):
        money_name(message)


@bot.message_handler(commands=features_offers+features_oners+features_defaulters)
def chat_options_handler(message):
    log.log_print("chat_options_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message, message.from_user, "chat_changer"):
        chat_options(message)


@bot.message_handler(commands=system_features_oners+system_features_offers)
def system_options_handler(message):
    log.log_print("system_options_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message, message.from_user, "chat_changer"):
        system_options(message)


'''
@bot.message_handler(commands=['change_database'])
def database_changer_handler(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    log.log_print(f"{__name__} invoked")
    if rank_required(message, "Deputy"):
        database_changer()
'''

'''Составные команды'''


@bot.callback_query_handler(func=lambda call: call.data == 'captcha')
def captcha_completed_handler(call):
    log.log_print("captcha_completed_handler invoked")
    captcha_completed(call)


@bot.callback_query_handler(func=lambda call: call.data == 'captcha_fail')
def captcha_failed_handler(call):
    log.log_print("captcha_failed_handler invoked")
    captcha_failed(call)


@bot.callback_query_handler(func=lambda call: 'adequate' in call.data and call.data != 'inadequate')
def adequate_handler(call):
    """Вариант адекватен"""
    log.log_print(f"adequate_handler invoked")
    adequate(call)


@bot.callback_query_handler(func=lambda call: call.data == 'inadequate')
def inadequate_handler(call):
    """Вариант неадекватен"""
    log.log_print(f"inadequate_handler invoked")
    inadequate(call)


@bot.inline_handler(lambda query: query.query == 'test')
def response_handler(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    log.log_print(f"response_handler invoked")
    response(inline_query)


@bot.message_handler(regexp='Признаю оскорблением')
def insult_handler(message):  # TODO В частных чатах бот не умеет указать ссылку нормально
    # TODO Проверка на наличие админосостава
    """Спращивает, иронично ли признание оскорблением"""
    log.log_print(f"insult_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message, message.from_user, "standart"):
        insult(message)


@bot.callback_query_handler(func=lambda call: call.data == 'non_ironic')  # триггерится, когда нажата кнопка "Нет"
def non_ironic_handler(call):
    """Реакция, если обвинение было неироничным"""
    log.log_print(f"non_ironic_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        non_ironic(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.callback_query_handler(func=lambda call: call.data == 'ironic')  # триггерится, когда нажата кнопка "Да"
def ironic_handler(call):
    """Реакция, если обвинение было ироничным"""
    log.log_print(f"ironic_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        ironic(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.message_handler(commands=['vote', 'multi_vote', 'adapt_vote'])
def vote_handler(message):
    """Генерирует голосовашку"""
    log.log_print(f"vote_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        vote(message)


@bot.callback_query_handler(func=lambda call: 'here' in call.data or 'nedostream' in call.data)
def place_here_handler(call):
    """Выбирает, куда прислать голосовашку"""
    log.log_print(f"place_here_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        place_here(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@bot.callback_query_handler(func=lambda call: 'mv_' in call.data)
def mv_handler(call):
    """Обновляет мульти-голосовашку"""
    log.log_print(f"mv_handler invoked")
    # TODO Убрать привязку к МФным голосовашкам
    if call.chat_instance != "-8294084429973252853" or is_suitable(call, call.from_user, "advanced"):
        mv(call)


@bot.callback_query_handler(func=lambda call: 'av_' in call.data)
def av_handler(call):
    """Обновляет адапт-голосовашку"""
    log.log_print(f"av_handler invoked")
    if call.chat_instance != "-8294084429973252853" or is_suitable(call, call.from_user, "advanced"):
        av(call)


@bot.callback_query_handler(func=lambda call: call.data == 'favor' or call.data == 'against' or call.data == 'abstain')
def add_vote_handler(call):
    """Вставляет голос в голосоовашку"""
    log.log_print("add_vote_handler invoked")
    if call.chat_instance != "-8294084429973252853" or is_suitable(call, call.from_user, "advanced"):
        add_vote(call)


'''Простые команды и старт'''


# TODO Это блять не простая команда, а админская
@bot.message_handler(commands=['lang'])
def language_getter_handler(message):
    """Gets the language of the chat"""
    log.log_print("language_getter_handler invoked")  # TODO Более удобную ставилку языков
    if in_mf(message, command_type=None, or_private=True):
        if message.chat.id > 0 or is_suitable(message, message.from_user, 'boss'):
            language_getter(message)


@bot.message_handler(commands=['start'])
def starter_handler(message):
    """Запуск бота в личке, в чате просто реагирует"""
    log.log_print("starter_handler invoked")
    if is_correct_message(message) and in_mf(message, command_type=None):
        starter(message)


@bot.message_handler(commands=['help'])
def helper_handler(message):
    """Предоставляет человеку список команд"""
    log.log_print("helper_handler invoked")
    if is_correct_message(message) and in_mf(message, command_type=None):
        helper(message)


@bot.message_handler(commands=['money_help', 'help_money'])
def money_helper_handler(message):
    """Financial instructions"""
    log.log_print("money_helper_handler invoked")
    if in_mf(message, command_type=None):
        money_helper(message)


@bot.message_handler(commands=['id'])
def show_id_handler(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    log.log_print(f"show_id_handler invoked")
    if in_mf(message, command_type=None):
        developer_commands.show_id(message)


@bot.message_handler(commands=['echo'])
def echo_message_handler(message):
    log.log_print(f"echo_message_handler invoked")
    if in_mf(message, command_type=None):
        developer_commands.echo_message(message)


@bot.message_handler(commands=['clear'])
def echo_message_handler(message):
    log.log_print(f"clear_echo_message_handler invoked")
    if in_mf(message, command_type=None):
        developer_commands.clear_echo_message(message)


@bot.message_handler(commands=['html'])
def echo_message_handler(message):
    log.log_print("html_echo_message_handler invoked")
    if in_mf(message, command_type=None):
        developer_commands.html_echo_message(message)


@bot.message_handler(commands=['minet', 'french_style_sex', 'blowjob'])
def minet_handler(message):
    """Приносит удовольствие"""
    log.log_print(f"minet_handler invoked")
    if is_correct_message(message) and in_mf(message, 'standart_commands') and cooldown(message, 'minet'):
        minet(message)


@bot.message_handler(commands=['drakken', 'art'])
def send_stuff_from_storage_handler(message):
    """Send random media from the storage"""
    log.log_print("send_stuff_from_storage_handler invoked")
    command = remove_slash_and_bot_mention(message.text)
    if in_mf(message, 'standart_commands') and cooldown(message, command):
        send_stuff_from_storage(message, command)


@bot.message_handler(commands=['breasts', 'ass'])
def send_vulgar_stuff_from_storage_handler(message):
    log.log_print("send_vulgar_stuff_from_storage_handler invoked")
    command = remove_slash_and_bot_mention(message.text)
    if in_mf(message, 'erotic_commands') and cooldown(message, command, timeout=60):
        send_stuff_from_storage(message, command)


@bot.message_handler(regexp='есть один мем')
@bot.message_handler(commands=['meme'])
def send_meme_handler(message):
    """Присылает мем"""
    log.log_print(f"send_meme_handler invoked")
    if in_mf(message, 'standart_commands') and cooldown(message, 'meme'):
        send_meme(message)


@bot.message_handler(commands=['me', 'check', 'check_me', 'check_ebalo'])
def send_me_handler(message):
    """Присылает человеку его запись в БД"""
    log.log_print(f"send_me_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        person = person_analyze(message, to_self=True)
        if person:
            send_me(message, person)


@bot.message_handler(commands=['members', 'database'])
def all_members_handler(message):
    """Присылает человеку все записи в БД"""
    log.log_print(f"all_members_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        send_some_top(message, '{index}. <code>{p_id}</code> {p_link}\n')


@bot.message_handler(commands=['give'])
def money_give_handler(message):
    """Обмен денег между пользователями"""
    log.log_print(f"money_give_handler invoked")
    if in_mf(message, 'financial_commands', or_private=False):
        person = person_analyze(message, to_bot=False)
        if person:
            if int_check(message.text.split()[-1], positive=False):
                money_give(message, person)
            else:
                reply(message, "Последнее слово должно быть числом, сколько денег даём")


@bot.message_handler(commands=['top'])
def money_top_handler(message):
    """Топ ЯМ"""
    log.log_print("money_top_handler invoked")
    if in_mf(message, 'financial_commands', or_private=False):
        send_some_top(message, '{index}. {p_link} — {money} {m_emo}\n', start='Бюджет: {bot_money} {m_emo}\n\n',
                      sort_by_what='money', to_private=False)


@bot.message_handler(commands=['messages_top'])
def messages_top_handler(message):
    """Messages top"""
    log.log_print("messages_top_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        # messages_top(message)
        send_some_top(message, '{index}. {p_link} — {messages} сообщ.\n', sort_by_what='messages', min_value=10)


@bot.message_handler(commands=['month'])
def month_set_handler(message):
    """Set month of person's birthday"""
    log.log_print("month_set_handler invoked")
    if in_mf(message, command_type=None):
        month = int_check(message.text.split()[-1], positive=True)
        if month and 1 <= month <= 12:
            month_set(message, month)
        else:
            reply(message, "Последнее слово должно быть положительным числом от 1 до 12 — номером месяца")


@bot.message_handler(commands=['day'])
def day_set_handler(message):
    """Set day of person's birthday"""
    log.log_print("day_set_handler invoked")
    if in_mf(message, command_type=None):
        day = int_check(message.text.split()[-1], positive=True)
        if day and 1 <= day <= 31:
            day_set(message, day)
        else:
            reply(message, "Последнее слово должно быть положительным числом от 1 до 31 — номером дня")


@bot.message_handler(commands=['bdays', 'birthdays'])
def birthday_handler(message):
    """Show the nearest birthdays"""
    log.log_print(f"birthday_handler invoked")
    if in_mf(message, command_type=None):
        birthday(message)


@bot.message_handler(commands=['admins', 'report'])
def admins_handler(message):
    """Ping admins"""
    log.log_print("admins_handler invoked")
    if in_mf(message, command_type=None) and is_suitable(message, message.from_user, "standart")\
            and cooldown(message, 'admins', 300):
        admins(message)


@bot.message_handler(commands=['chat'])
def chat_check_handler(message):
    """Show options of the current chat"""
    log.log_print("chat_check_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        chat_check(message)


@bot.message_handler(commands=['system'])
def system_check_handler(message):
    """Show options of the current chat"""
    log.log_print("system_check_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        system_check(message)


'''
@bot.message_handler(commands=['chats'])
def chats_handler(message):
    """Send chat list"""
    if in_mf(message, 'standart_commands'):
        chats(message)
'''


@bot.message_handler(commands=['anon'])
def anon_message_handler(message):
    """Send anon message to admin place"""
    log.log_print("anon_message_handler invoked")
    if message.chat.id > 0:
        if len(message.text) == 5:
            reply(message, "После команды /anon должно следовать то, что надо отправить админам")
        else:
            anon_message(message)
    else:
        reply(message, "Эта команда предназначена для лички")


@bot.message_handler(commands=['test'])
def database_send_handler(message):
    log.log_print('database_send_handler invoked')
    if message.chat.id == 381279599:
        for FILE in (database_file, votes_file, adapt_votes_file, multi_votes_file, systems_file, storage_file):
            file_send = open(FILE, 'rb')
            send_document(message.chat.id, file_send)
            file_send.close()


'''Последний хэндлер. Просто считает сообщения, что не попали в другие хэндлеры'''


@bot.message_handler(func=lambda message: True, content_types=all_content_types)
def counter_handler(message):
    """Подсчитывает сообщения"""
    log.log_print("counter_handler invoked")
    global new_dudes
    if in_mf(message, command_type=None, loud=False, or_private=False):
        reactions.trigger(message)
        if message.from_user.id in new_dudes:
            new_dudes[message.from_user.id].append(message.message_id)
            if len(new_dudes[message.from_user.id]) == 5:
                new_dudes.pop(message.from_user.id)
            print(new_dudes)
