""" All bot message and call handlers are here """
from random import shuffle

from presenter.config.token import BOT
from presenter.config.log import Logger, LOG_TO
from presenter.config import config_func
from presenter.logic import (boss_commands, complicated_commands, reactions, standart_commands,
                             developer_commands)
from presenter.config import config_var, files_paths
from presenter.logic.elite import elite
from presenter.logic.start import starter
from view import output

LOG = Logger(LOG_TO)
WORK = True

# Реакции на медиа, новых участников и выход участников


@BOT.message_handler(content_types=['migrate_from_chat_id'])
def chat_id_update_handler(message):
    """ Update chat ID """
    LOG.log_print("chat_id_update_handler invoked")
    reactions.chat_id_update(message)


@BOT.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    """Реагирует на вход в чат"""
    LOG.log_print("new_member_handler invoked")
    person = message.new_chat_members[0]
    if config_func.in_mf(message, command_type=None, or_private=False):
        reactions.new_member(message, person)


@BOT.message_handler(content_types=['left_chat_member'])
def left_member_handler(message):
    """Комментирует уход участника и прощается участником"""
    LOG.log_print("left_member_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False, loud=False):
        reactions.left_member(message)


# Элитарные команды


@BOT.message_handler(commands=['elite'])
def elite_handler(message):
    """ Runs an Elite test """
    LOG.log_print("elite_handler invoked")
    if message.chat.type == 'private':  # Тест на элитность можно провести только в личке у бота
        elite(message)
    else:
        output.reply(message, "Напиши мне это в личку, я в чате не буду этим заниматься")


# Админские обычные команды


@BOT.message_handler(commands=['add'])
def upload_stuff_to_storage_handler(message):
    """ Add stuff to a media storage """
    LOG.log_print("upload_stuff_to_storage_handler invoked")
    analyzer = config_func.Analyzer(message, value_necessary=False)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, command_type=None):
        if config_func.check_access_to_a_storage(message, storage_name, is_write_mode=True):
            boss_commands.add_stuff_to_storage(message, storage_name)


@BOT.message_handler(commands=['remove'])
def remove_stuff_from_storage_handler(message):
    """Removes some media from media storage"""
    LOG.log_print("remove_stuff_from_storage_handler invoked")
    analyzer = config_func.Analyzer(message, value_necessary=False)
    comment = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, command_type=None):
        list_of_words = comment.split()
        if len(list_of_words) >= 2:
            storage_name = list_of_words[0]
            file_id = list_of_words[1]
            if config_func.check_access_to_a_storage(message, storage_name, is_write_mode=True):
                boss_commands.remove_stuff_from_storage(message, storage_name, file_id)
        else:
            output.reply(message, "Нужно название хранилища и ID файла")


@BOT.message_handler(commands=['create'])
def create_new_storage_handler(message):
    """ Creates new media storage """
    LOG.log_print('create_new_storage_handler invoked')
    analyzer = config_func.Analyzer(message, value_necessary=False)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, command_type=None):
        if message.from_user.id == config_var.CREATOR_ID:
            if storage_name:
                boss_commands.create_new_storage(message, storage_name, False)
            else:
                output.reply(message, "Не хватает названия")
        else:
            output.reply(message, "Эта команда только для моего хозяина")


@BOT.message_handler(commands=['create_vulgar'])
def create_new_vulgar_storage_handler(message):
    """ Creates new vulgar media storage """
    LOG.log_print('create_new_vulgar_storage_handler invoked')
    analyzer = config_func.Analyzer(message, value_necessary=False)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, command_type=None):
        if message.from_user.id == config_var.CREATOR_ID:
            if storage_name:
                boss_commands.create_new_storage(message, storage_name, True)
            else:
                output.reply(message, "Не хватает названия")
        else:
            output.reply(message, "Эта команда только для моего хозяина")


@BOT.message_handler(commands=['add_moder'])
def add_moderator_to_storage_handler(message):
    """ Adds a moderator to a storage """
    LOG.log_print('add_moderator_to_storage_handler invoked')
    analyzer = config_func.Analyzer(message, value_necessary=False)
    person = analyzer.return_target_person(to_self=True)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, command_type=None) and person and \
            config_func.check_access_to_a_storage(message, storage_name, False):
        if message.from_user.id == config_var.CREATOR_ID:
            # TODO function is_demax, checks if demax uses it + says if it is demax only
            boss_commands.add_moderator_to_storage(message, storage_name, person.id)
        else:
            output.reply(message, "Эта команда только для моего хозяина")


@BOT.message_handler(commands=['remove_moder'])
def remove_moderator_from_storage_handler(message):
    """ Removes a moderator from a storage """
    LOG.log_print('remove_moderator_from_storage_handler invoked')
    analyzer = config_func.Analyzer(message, value_necessary=False)
    person = analyzer.return_target_person(to_self=True)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, command_type=None) and person and \
            config_func.check_access_to_a_storage(message, storage_name, False):
        if message.from_user.id == config_var.CREATOR_ID:
            boss_commands.remove_moderator_from_storage(message, storage_name, person.id)
        else:
            output.reply(message, "Эта команда только для моего хозяина")


@BOT.message_handler(commands=['update'])
def update_all_members_handler(message):
    """ Updates members database """
    LOG.log_print("update_all_members_handler invoked")
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        boss_commands.update_all_members(message)


@BOT.message_handler(commands=['warn'])
def warn_handler(message):
    """Даёт участнику предупреждение"""
    LOG.log_print("warn_handler invoked")
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        rep = message.reply_to_message
        if rep:
            analyzer = config_func.Analyzer(message, default_value=1, value_positive=True)
            parameters_dictionary = analyzer.parameters_dictionary
            if analyzer.check_person(rep.from_user, False, False) \
                    and config_func.rank_superiority(message, rep.from_user):
                if parameters_dictionary:
                    boss_commands.warn(message, rep.from_user, parameters_dictionary)
        else:
            output.reply(
                message, "Надо ответить на сообщение с актом преступления, чтобы переслать контекст\
                          в хранилище")


@BOT.message_handler(commands=['unwarn'])
def unwarn_handler(message):
    """Снимает с участника предупреждение"""
    LOG.log_print("unwarn_handler invoked")
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        analyzer = config_func.Analyzer(message, default_value=1, value_positive=True)
        person = analyzer.return_target_person()
        if person:
            boss_commands.unwarn(message, person, analyzer.parameters_dictionary)


@BOT.message_handler(commands=['ban'])
def ban_handler(message):
    """ Ban member """
    LOG.log_print(f"ban_handler invoked")
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person()
        if person and config_func.rank_superiority(message, person):
            boss_commands.ban(message, person)


@BOT.message_handler(commands=['kick'])
def kick_handler(message):
    """ Kicks member """
    LOG.log_print(f"kick_handler invoked")
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person()
        if person and config_func.rank_superiority(message, person):
            boss_commands.ban(message, person, unban_then=True)


@BOT.message_handler(commands=['mute'])
def mute_handler(message):
    """ Mutes member """
    LOG.log_print("mute_handler invoked")
    if config_func.in_mf(message, "boss_commands", or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        analyzer = config_func.Analyzer(message, default_value=1, value_positive=True)
        person = analyzer.return_target_person()
        parameters_dictionary = analyzer.parameters_dictionary
        if person and config_func.rank_superiority(message, person) and parameters_dictionary:
            boss_commands.mute(message, person, parameters_dictionary)


@BOT.message_handler(commands=['pay'])
def money_pay_handler(message):
    """ Give money from the treasury to the member """
    LOG.log_print(f"money_pay_handler invoked")
    if config_func.in_mf(message, 'financial_commands', or_private=False) \
            and config_func.is_suitable(message, message.from_user, 'boss'):
        analyzer = config_func.Analyzer(message)
        person = analyzer.return_target_person(to_self=True)
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            boss_commands.money_pay(message, person, parameters_dictionary)


@BOT.message_handler(func=config_func.in_system_commands)
def rank_changer_handler(message):
    """Changes person's rank"""
    LOG.log_print("rank_changer_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False):
        # TODO Сделать так, чтоб добавлять можно было только лидера
        if message.from_user.id == config_var.CREATOR_ID:
            person = config_func.Analyzer(message, value_necessary=False).return_target_person()
            if person:
                boss_commands.rank_changer(message, person)
        elif config_func.is_suitable(message, message.from_user, 'uber'):
            person = config_func.Analyzer(message, value_necessary=False).return_target_person()
            if person and config_func.rank_superiority(message, person):
                boss_commands.rank_changer(message, person)


@BOT.message_handler(commands=['messages'])
def messages_change_handler(message):
    """Меняет запись в БД о количестве сообщений чела"""
    LOG.log_print(f"messages_change_handler invoked")
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, "boss"):
        analyzer = config_func.Analyzer(message, value_positive=True)
        person = analyzer.return_target_person(to_self=True)
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            boss_commands.message_change(message, person, parameters_dictionary)


@BOT.message_handler(commands=['add_chat'])
def add_chat_handler(message):  # TODO Она работает в личке, а не должна
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    LOG.log_print(f"add_chat_handler invoked")
    boss_commands.add_chat(message)


@BOT.message_handler(commands=['del_chat'])
def del_chat_handler(message):
    """Removes chat from the system."""
    LOG.log_print('del_chat_handler invoked')
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.del_chat(message)


@BOT.message_handler(commands=['admin_place'])
def add_admin_place_handler(message):
    """Add admin place to system"""
    LOG.log_print("add_admin_place_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.add_admin_place(message)


@BOT.message_handler(commands=['money_on', 'money_off'])
def money_mode_change_handler(message):
    """ Enable or disable money system """
    LOG.log_print("money_mode_change_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.money_mode_change(message)


@BOT.message_handler(commands=['money_reset'])
def money_reset_handler(message):
    """Take all users' money to a system fund"""
    LOG.log_print("money_reset_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.money_reset(message)


@BOT.message_handler(commands=['m_emoji'])
def money_emoji_handler(message):
    """ Put emoji to indicate the amount of currency """
    LOG.log_print("money_emoji_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.money_emoji(message)


@BOT.message_handler(commands=['m_name'])
def money_name_handler(message):
    """ Set currency name """
    LOG.log_print("money_name_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.set_money_name(message)


@BOT.message_handler(commands=config_var.FEATURES_OFFERS + config_var.FEATURES_ONERS +
                     config_var.FEATURES_DEFAULTERS)
def chat_options_handler(message):
    """ Change chat options """
    LOG.log_print("chat_options_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.chat_options(message)


@BOT.message_handler(commands=['standart_greetings'])
def update_standart_greetings_handler(message):
    """ Change standart greeting """
    LOG.log_print("update_standart_greetings_handler invoked")
    if config_func.in_mf(message, command_type=False, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.update_greetings_json(message, 'standart')


@BOT.message_handler(commands=['captcha_greetings'])
def update_captcha_greetings_handler(message):
    """ Change captcha greeting """
    LOG.log_print("update_captcha_greetings_handler invoked")
    if config_func.in_mf(message, command_type=False, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.update_greetings_json(message, 'captcha')


@BOT.message_handler(commands=['admin_greetings'])
def update_admin_greetings_handler(message):
    """ Change admin's greeting """
    LOG.log_print("update_admin_greetings_handler invoked")
    if config_func.in_mf(message, command_type=False, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.update_greetings_json(message, 'admin')


@BOT.message_handler(commands=['full_admin_greetings'])
def update_full_admin_greetings_handler(message):
    """ Change full admin's greeting """
    LOG.log_print("update_full_admin_greetings_handler invoked")
    if config_func.in_mf(message, command_type=False, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.update_greetings_json(message, 'full_admin')


@BOT.message_handler(commands=config_var.SYSTEM_FEATURES_ONERS + config_var.SYSTEM_FEATURES_OFFERS)
def system_options_handler(message):
    """ Change chat system options """
    LOG.log_print("system_options_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.system_options(message)


# @bot.message_handler(commands=['change_database'])
# def database_changer_handler(message):
#     """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
#     LOG.log_print(f"{__name__} invoked")
#     if rank_required(message, "Deputy"):
#         database_changer()

# Составные команды


@BOT.callback_query_handler(func=lambda call: call.data == 'captcha')
def captcha_completed_handler(call):
    """ It is executing when new member passes the captcha """
    LOG.log_print("captcha_completed_handler invoked")
    complicated_commands.captcha_completed(call)


@BOT.callback_query_handler(func=lambda call: call.data == 'captcha_fail')
def captcha_failed_handler(call):
    """ It is executing when new member fails the captcha """
    LOG.log_print("captcha_failed_handler invoked")
    complicated_commands.captcha_failed(call)


@BOT.callback_query_handler(func=lambda call: 'adequate' in call.data and call.data != 'inadequate')
def adequate_handler(call):
    """Вариант адекватен"""
    LOG.log_print(f"adequate_handler invoked")
    complicated_commands.adequate(call)


@BOT.callback_query_handler(func=lambda call: call.data == 'inadequate')
def inadequate_handler(call):
    """Вариант неадекватен"""
    LOG.log_print(f"inadequate_handler invoked")
    complicated_commands.inadequate(call)


@BOT.inline_handler(lambda query: query.query == 'test')
def response_handler(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    LOG.log_print(f"response_handler invoked")
    complicated_commands.response(inline_query)


@BOT.message_handler(regexp='Признаю оскорблением')
def insult_handler(message):  # TODO В частных чатах бот не умеет указать ссылку нормально
    # TODO Проверка на наличие админосостава
    """Спращивает, иронично ли признание оскорблением"""
    LOG.log_print(f"insult_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "standart"):
        complicated_commands.insult(message)


@BOT.callback_query_handler(func=lambda call: call.data == 'non_ironic'
                            )  # триггерится, когда нажата кнопка "Нет"
def non_ironic_handler(call):
    """Реакция, если обвинение было неироничным"""
    LOG.log_print(f"non_ironic_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        complicated_commands.non_ironic(call)
    else:
        output.answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.callback_query_handler(func=lambda call: call.data == 'ironic'
                            )  # триггерится, когда нажата кнопка "Да"
def ironic_handler(call):
    """Реакция, если обвинение было ироничным"""
    LOG.log_print(f"ironic_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        complicated_commands.ironic(call)
    else:
        output.answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.message_handler(commands=['vote', 'multi_vote', 'adapt_vote'])
def vote_handler(message):
    """Генерирует голосовашку"""
    LOG.log_print(f"vote_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False):
        complicated_commands.vote(message)


@BOT.callback_query_handler(func=lambda call: 'here' in call.data or 'nedostream' in call.data)
def place_here_handler(call):
    """Выбирает, куда прислать голосовашку"""
    LOG.log_print(f"place_here_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        complicated_commands.place_here(call)
    else:
        output.answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.callback_query_handler(func=lambda call: 'mv_' in call.data)
def mv_handler(call):
    """Обновляет мульти-голосовашку"""
    LOG.log_print(f"mv_handler invoked")
    # TODO Убрать привязку к МФным голосовашкам
    if call.chat_instance != "-8294084429973252853" or config_func.is_suitable(
            call, call.from_user, "advanced"):
        complicated_commands.multi_vote(call)


@BOT.callback_query_handler(func=lambda call: 'av_' in call.data)
def av_handler(call):
    """Обновляет адапт-голосовашку"""
    LOG.log_print(f"av_handler invoked")
    if call.chat_instance != "-8294084429973252853" or config_func.is_suitable(
            call, call.from_user, "advanced"):
        complicated_commands.adapt_vote(call)


@BOT.callback_query_handler(
    func=lambda call: call.data == 'favor' or call.data == 'against' or call.data == 'abstain')
def add_vote_handler(call):
    """Вставляет голос в голосоовашку"""
    LOG.log_print("add_vote_handler invoked")
    if call.chat_instance != "-8294084429973252853" or config_func.is_suitable(
            call, call.from_user, "advanced"):
        complicated_commands.add_vote(call)


# Простые команды и старт


# TODO Это блять не простая команда, а админская
@BOT.message_handler(commands=['lang'])
def language_getter_handler(message):
    """Gets the language of the chat"""
    LOG.log_print("language_getter_handler invoked")  # TODO Более удобную ставилку языков
    if config_func.in_mf(message, command_type=None, or_private=True):
        if message.chat.id > 0 or config_func.is_suitable(message, message.from_user, 'boss'):
            standart_commands.language_setter(message)


@BOT.message_handler(commands=['start'])
def starter_handler(message):
    """Запуск бота в личке, в чате просто реагирует"""
    LOG.log_print("starter_handler invoked")
    if config_func.is_correct_message(message) and config_func.in_mf(message, command_type=None):
        starter(message)


@BOT.message_handler(commands=['help'])
def helper_handler(message):
    """Предоставляет человеку список команд"""
    LOG.log_print("helper_handler invoked")
    if config_func.is_correct_message(message) and config_func.in_mf(message, command_type=None):
        standart_commands.helper(message)


@BOT.message_handler(commands=['money_help', 'help_money'])
def money_helper_handler(message):
    """Financial instructions"""
    LOG.log_print("money_helper_handler invoked")
    if config_func.in_mf(message, command_type=None):
        standart_commands.money_helper(message)


@BOT.message_handler(commands=['storages'])
def send_list_of_storages_handler(message):
    """ Sends list of all storages """
    LOG.log_print("send_list_of_storages_handler invoked")
    if config_func.in_mf(message, command_type=None):
        standart_commands.send_list_of_storages(message)


@BOT.message_handler(commands=['id'])
def show_id_handler(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    LOG.log_print(f"show_id_handler invoked")
    if config_func.in_mf(message, command_type=None):
        developer_commands.show_id(message)


@BOT.message_handler(commands=['echo'])
def echo_message_handler(message):
    """ Repeats message """
    LOG.log_print("echo_message_handler invoked")
    if config_func.in_mf(message, command_type=None):
        developer_commands.echo_message(message)


@BOT.message_handler(commands=['clear'])
def clear_echo_message_handler(message):
    """ Clears echo messages """
    LOG.log_print("clear_echo_message_handler invoked")
    if config_func.in_mf(message, command_type=None):
        developer_commands.clear_echo_message(message)


@BOT.message_handler(commands=['html'])
def html_echo_message_handler(message):
    """ Repeats message with HTML message markup """
    LOG.log_print("html_echo_message_handler invoked")
    if config_func.in_mf(message, command_type=None):
        developer_commands.html_echo_message(message)


@BOT.message_handler(commands=['rights'])
def rights_handler(message):
    """ Check bot rights """
    LOG.log_print("rights_handler invoked")
    if config_func.in_mf(message, command_type=None):
        developer_commands.get_bot_rights(message)


@BOT.message_handler(commands=['minet', 'french_style_sex', 'blowjob'])
def minet_handler(message):
    """Приносит удовольствие"""
    LOG.log_print(f"minet_handler invoked")
    if config_func.is_correct_message(message) and config_func.in_mf(message, 'standart_commands'):
        language = config_func.get_one_language(message)
        if language and config_func.cooldown(message, 'minet'):
            standart_commands.minet(message, language)


@BOT.message_handler(commands=['shuffle'])
def shuffle_handler(message):
    """ Shuffle a list """
    LOG.log_print("shuffle_handler invoked")
    if config_func.in_mf(message, 'standart_commands'):
        analyzer = config_func.Analyzer(message, value_necessary=False)
        elements = analyzer.parameters_dictionary['comment'].split()
        if not elements:
            output.reply(message, 'Пожалуйста, напишите список, а элементы списка разделите пробелом')
        shuffle(elements)
        if 'value' in analyzer.parameters_dictionary:
            elements = elements[:analyzer.parameters_dictionary['value']]
        out = '\n'.join(f'{i + 1}. {j}' for i, j in enumerate(elements))
        output.reply(message, out)


@BOT.message_handler(commands=['get'])
def send_stuff_from_storage_handler(message):
    """Send random media from the storage"""
    LOG.log_print("send_stuff_from_storage_handler invoked")
    analyzer = config_func.Analyzer(message, value_necessary=False)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, 'standart_commands') and config_func.check_access_to_a_storage(
            message, storage_name, False) and config_func.cooldown(message, storage_name,
                                                                   timeout=300):
        if "value" in analyzer.parameters_dictionary:
            stuff_number = analyzer.parameters_dictionary["value"]
            standart_commands.send_numbered_stuff_from_storage(message, storage_name, stuff_number)
        else:
            standart_commands.send_random_stuff_from_storage(message, storage_name)


@BOT.message_handler(commands=['size'])
def check_storage_size_handler(message):
    """ Checks how many moderators and how much media there is in a storage """
    LOG.log_print('check_storage_size_handler invoked')
    analyzer = config_func.Analyzer(message, value_necessary=False)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, 'standart_commands') and config_func.check_access_to_a_storage(
            message, storage_name, False, to_check_vulgarity=False):
        standart_commands.check_storage_size(message, storage_name)


@BOT.message_handler(regexp='есть один мем')
@BOT.message_handler(commands=['meme'])
def send_meme_handler(message):
    """Присылает мем"""
    LOG.log_print(f"send_meme_handler invoked")
    if config_func.in_mf(message, 'standart_commands') and config_func.cooldown(message, 'meme'):
        standart_commands.send_meme(message)


@BOT.message_handler(commands=['me', 'check', 'check_me', 'check_ebalo'])
def send_me_handler(message):
    """Присылает человеку его запись в БД"""
    LOG.log_print(f"send_me_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False):
        person = config_func.Analyzer(message,
                                      value_necessary=False).return_target_person(to_self=True)
        if person:
            standart_commands.send_me(message, person)


@BOT.message_handler(commands=['members'])
def all_members_handler(message):
    """Присылает человеку все записи в БД"""
    LOG.log_print("all_members_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False):
        language = config_func.get_one_language(message)
        if language:
            if config_func.is_suitable(message, message.from_user, 'boss', loud=False):
                standart_commands.send_some_top(message, language,
                                                '{index}. <code>{id}</code> {p_link}\n')
            else:
                standart_commands.send_some_top(message, language,
                                                '{index}. <code>{id}</code> {nickname}\n')


@BOT.message_handler(commands=['give'])
def money_give_handler(message):
    """Обмен денег между пользователями"""
    LOG.log_print(f"money_give_handler invoked")
    if config_func.in_mf(message, 'financial_commands', or_private=False):
        analyzer = config_func.Analyzer(message)
        person = analyzer.return_target_person()
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            standart_commands.money_give(message, person, parameters_dictionary)


@BOT.message_handler(commands=['fund'])
def money_fund_handler(message):
    """Transfer money to the chat fund"""
    LOG.log_print(f"money_fund_handler invoked")
    if config_func.in_mf(message, 'financial_commands', or_private=False):
        analyzer = config_func.Analyzer(message)
        parameters_dictionary = analyzer.parameters_dictionary
        if parameters_dictionary:
            standart_commands.money_fund(message, parameters_dictionary)


@BOT.message_handler(commands=['top', 'money_top'])
def money_top_handler(message):
    """Топ ЯМ"""
    LOG.log_print("money_top_handler invoked")
    if config_func.in_mf(message, 'financial_commands', or_private=False):
        language = config_func.get_one_language(message)
        if language:
            args = message, language, '{index}. {p_link} — {money} {m_emo}\n'
            kwargs = {'start': 'Бюджет: {bot_money} {m_emo}\n\n', 'sort_key': lambda x: x['money']}
            if config_func.is_suitable(message, message.from_user, 'boss', loud=False):
                standart_commands.send_some_top(*args, **kwargs)
            else:
                standart_commands.send_short_top(*args, **kwargs)


@BOT.message_handler(commands=['warns'])
def warns_top_handler(message):
    """ Show all warns """
    LOG.log_print('warns_top_handler invoked')
    if config_func.in_mf(message, command_type=None, or_private=False):
        language = config_func.get_one_language(message)
        if language:
            args = message, language, '{index}. {p_link} — {warns} ⛔️\n'
            kwargs = {'start': 'Количество варнов:\n\n', 'sort_key': lambda x: x['warns']}
            standart_commands.send_some_top(*args, **kwargs)


@BOT.message_handler(commands=['messages_top'])
def messages_top_handler(message):
    """Messages top"""
    LOG.log_print("messages_top_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False):
        language = config_func.get_one_language(message)
        if language:
            args = message, language, '{index}. {p_link} — {messages} сообщ.\n'
            kwargs = {'sort_key': lambda x: x['messages']}
            if config_func.is_suitable(message, message.from_user, 'boss', loud=False):
                standart_commands.send_some_top(*args, **kwargs)
            else:
                standart_commands.send_short_top(*args, **kwargs)


@BOT.message_handler(commands=['month'])
def month_set_handler(message):
    """Set month of person's birthday"""
    LOG.log_print("month_set_handler invoked")
    if config_func.in_mf(message, command_type=None):
        month = config_func.int_check(message.text.split()[-1], positive=True)
        if month and 1 <= month <= 12:
            standart_commands.month_set(message, month)
        else:
            output.reply(
                message, "Последнее слово должно быть положительным числом от 1 до 12 — "
                         "номером месяца")


@BOT.message_handler(commands=['day'])
def day_set_handler(message):
    """Set day of person's birthday"""
    LOG.log_print("day_set_handler invoked")
    if config_func.in_mf(message, command_type=None):
        day = config_func.int_check(message.text.split()[-1], positive=True)
        if day and 1 <= day <= 31:
            language = config_func.get_one_language(message)
            if language:
                standart_commands.day_set(message, day, language)
        else:
            output.reply(
                message, "Последнее слово должно быть положительным числом от 1 до 31 — "
                         "номером дня")


@BOT.message_handler(commands=['bdays', 'birthdays'])
def birthday_handler(message):
    """Show the nearest birthdays"""
    LOG.log_print(f"birthday_handler invoked")
    if config_func.in_mf(message, command_type=None):
        language = config_func.get_one_language(message)
        if language:
            standart_commands.send_some_top(
                message,
                language,
                '{index}. {p_link} — {day} {month}\n',
                sort_key=lambda x: -100 * x['month_birthday'] - x['day_birthday'])


@BOT.message_handler(commands=['admins', 'report'])
def admins_handler(message):
    """Ping admins"""
    LOG.log_print("admins_handler invoked")
    if config_func.in_mf(message, command_type=None) and config_func.is_suitable(message,
                                                                                 message.from_user,
                                                                                 "standart") \
            and config_func.cooldown(message, 'admins', 300):
        standart_commands.admins(message)


@BOT.message_handler(commands=['chat'])
def chat_check_handler(message):
    """Show options of the current chat"""
    LOG.log_print("chat_check_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False):
        standart_commands.chat_check(message)


@BOT.message_handler(commands=['system'])
def system_check_handler(message):
    """Show options of the current chat"""
    LOG.log_print("system_check_handler invoked")
    if config_func.in_mf(message, command_type=None, or_private=False):
        standart_commands.system_check(message)


@BOT.message_handler(commands=['anon'])
def anon_message_handler(message):
    """Send anon message to admin place"""
    LOG.log_print("anon_message_handler invoked")
    if message.chat.id > 0:
        if len(message.text) == 5:
            output.reply(message,
                         "После команды /anon должно следовать то, что надо отправить админам")
        else:
            standart_commands.anon_message(message)
    else:
        output.reply(message, "Эта команда предназначена для лички")


@BOT.message_handler(commands=['test'])
def database_send_handler(message):
    """ Send all databases to config_var.CREATOR_ID """
    LOG.log_print('database_send_handler invoked')
    if message.chat.id == config_var.CREATOR_ID:
        for file in (
                files_paths.DATABASE_FILE, files_paths.VOTES_FILE,
                files_paths.ADAPT_VOTES_FILE, files_paths.MULTI_VOTES_FILE,
                files_paths.SYSTEMS_FILE, files_paths.STORAGE_FILE):
            file_send = open(file, 'rb')
            output.send_document(message.chat.id, file_send)
            file_send.close()


@BOT.message_handler(commands=['error'])
def simulate_error_handler(message):
    """Simulates an error"""
    if message.from_user.id == config_var.CREATOR_ID:
        developer_commands.simulate_error(message)
    else:
        output.reply(message, "Эта команда только для моего хозяина")


# Последний хэндлер. Просто считает сообщения, что не попали в другие хэндлеры


@BOT.message_handler(func=lambda message: True, content_types=config_var.ALL_CONTENT_TYPES)
def counter_handler(message):
    """Подсчитывает сообщения"""
    LOG.log_print("counter_handler invoked")
    if config_func.in_mf(message, command_type=None, loud=False, or_private=False):
        reactions.trigger(message)
