""" All bot message and call handlers are here """
from random import shuffle

from presenter.config.token_manager import BOT
from presenter.config.log import Logger, LOG_TO
from presenter.config import config_func
from presenter.logic import (boss_commands, complicated_commands, reactions, standard_commands,
                             developer_commands)
from presenter.config import config_var, files_paths
from presenter.logic.elite import elite, reset_test
from presenter.logic.start import starter
from view import output

LOG = Logger(LOG_TO)
WORK = True

# Реакции на медиа, новых участников и выход участников


@BOT.message_handler(content_types=['migrate_from_chat_id'])
@LOG.wrap
def chat_id_update_handler(message):
    """ Update chat ID """
    reactions.chat_id_update(message)


@BOT.message_handler(content_types=['new_chat_members'])
@LOG.wrap
def new_member_handler(message):
    """Реагирует на вход в чат"""
    person = message.new_chat_members[0]
    if config_func.in_mf(message, command_type=None, or_private=False):
        reactions.new_member(message, person)


@BOT.message_handler(content_types=['left_chat_member'])
@LOG.wrap
def left_member_handler(message):
    """Комментирует уход участника и прощается участником"""
    if config_func.in_mf(message, command_type=None, or_private=False, loud=False):
        reactions.left_member(message)


# Элитарные команды


@BOT.message_handler(commands=['elite'])
@LOG.wrap
def elite_handler(message):
    """ Runs an Elite test """
    if message.chat.type == 'private':  # Тест на элитность можно провести только в личке у бота
        elite(message)
    else:
        output.reply(message, "Напиши мне это в личку, я в чате не буду этим заниматься")


@BOT.message_handler(commands=["reset_elite", "reset_test"])
@LOG.wrap
def reset_test_handler(message):
    if message.from_user.id == config_var.CREATOR_ID:
        person = config_func.Analyzer(message, value_necessary=False).return_target_person(to_self=True)
        if person:
            reset_test(message, person)
    else:
        output.reply(message, "Это команда только для моего босса")


# Админские обычные команды


@BOT.message_handler(commands=['lang'])
@LOG.wrap
def language_getter_handler(message):
    """Gets the language of the chat"""
    if config_func.in_mf(message, command_type=None, or_private=True):
        if message.chat.id > 0 or config_func.is_suitable(message, message.from_user, 'boss'):
            boss_commands.language_setter(message)


@BOT.message_handler(commands=['add'])
@LOG.wrap
def upload_stuff_to_storage_handler(message):
    """ Add stuff to a media storage """
    analyzer = config_func.Analyzer(message, value_necessary=False)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, command_type=None):
        if config_func.check_access_to_a_storage(message, storage_name, is_write_mode=True):
            boss_commands.add_stuff_to_storage(message, storage_name)


@BOT.message_handler(commands=['remove'])
@LOG.wrap
def remove_stuff_from_storage_handler(message):
    """Removes some media from media storage"""
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
@LOG.wrap
def create_new_storage_handler(message):
    """ Creates new media storage """
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
@LOG.wrap
def create_new_vulgar_storage_handler(message):
    """ Creates new vulgar media storage """
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
@LOG.wrap
def add_moderator_to_storage_handler(message):
    """ Adds a moderator to a storage """
    analyzer = config_func.Analyzer(message, value_necessary=False)
    person = analyzer.return_target_person(to_self=True)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, command_type=None) and person and \
            config_func.check_access_to_a_storage(message, storage_name, False):
        if message.from_user.id == config_var.CREATOR_ID:
            boss_commands.add_moderator_to_storage(message, storage_name, person.id)
        else:
            output.reply(message, "Эта команда только для моего хозяина")


@BOT.message_handler(commands=['remove_moder'])
@LOG.wrap
def remove_moderator_from_storage_handler(message):
    """ Removes a moderator from a storage """
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
@LOG.wrap
def update_all_members_handler(message):
    """ Updates members database """
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        boss_commands.update_all_members(message)


@BOT.message_handler(commands=['warn'])
@LOG.wrap
def warn_handler(message):
    """Даёт участнику предупреждение"""
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
@LOG.wrap
def unwarn_handler(message):
    """Снимает с участника предупреждение"""
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        analyzer = config_func.Analyzer(message, default_value=1, value_positive=True)
        person = analyzer.return_target_person()
        if person:
            boss_commands.unwarn(message, person, analyzer.parameters_dictionary)


@BOT.message_handler(commands=['ban'])
@LOG.wrap
def ban_handler(message):
    """ Ban member """
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person()
        if person and config_func.rank_superiority(message, person):
            boss_commands.ban(message, person)


@BOT.message_handler(commands=['kick'])
@LOG.wrap
def kick_handler(message):
    """ Kicks member """
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person()
        if person and config_func.rank_superiority(message, person):
            boss_commands.ban(message, person, unban_then=True)


@BOT.message_handler(commands=['mute'])
@LOG.wrap
def mute_handler(message):
    """ Mutes member """
    if config_func.in_mf(message, "boss_commands", or_private=False) and config_func.is_suitable(
            message, message.from_user, 'boss'):
        analyzer = config_func.Analyzer(message, default_value=1, value_positive=True)
        person = analyzer.return_target_person()
        parameters_dictionary = analyzer.parameters_dictionary
        if person and config_func.rank_superiority(message, person) and parameters_dictionary:
            boss_commands.mute(message, person, parameters_dictionary)


@BOT.message_handler(commands=['pay'])
@LOG.wrap
def money_pay_handler(message):
    """ Give money from the treasury to the member """
    if config_func.in_mf(message, 'financial_commands', or_private=False) \
            and config_func.is_suitable(message, message.from_user, 'boss'):
        analyzer = config_func.Analyzer(message)
        person = analyzer.return_target_person(to_self=True)
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            boss_commands.money_pay(message, person, parameters_dictionary)


@BOT.message_handler(func=config_func.in_system_commands)
@LOG.wrap
def rank_changer_handler(message):
    """Changes person's rank"""
    if config_func.in_mf(message, command_type=None, or_private=False):
        if config_func.is_suitable(message, message.from_user, 'uber'):
            person = config_func.Analyzer(message, value_necessary=False).return_target_person(to_self=True)
            if person:
                if person.id == message.from_user.id or config_func.rank_superiority(message, person):
                    boss_commands.rank_changer(message, person)


@BOT.message_handler(commands=['messages'])
@LOG.wrap
def messages_change_handler(message):
    """Меняет запись в БД о количестве сообщений чела"""
    if config_func.in_mf(message, 'boss_commands', or_private=False) and config_func.is_suitable(
            message, message.from_user, "boss"):
        analyzer = config_func.Analyzer(message, value_positive=True)
        person = analyzer.return_target_person(to_self=True)
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            boss_commands.message_change(message, person, parameters_dictionary)


@BOT.message_handler(commands=['set_limit', 'limit_set'])
@LOG.wrap
def set_limit_handler(message):
    """Sets the limit for entering the chat"""
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        analyzer = config_func.Analyzer(message)
        parameters_dictionary = analyzer.parameters_dictionary
        if parameters_dictionary:
            boss_commands.set_limit(message, parameters_dictionary)


@BOT.message_handler(commands=['add_chat'])
@LOG.wrap
def add_chat_handler(message):
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    if message.chat.id < 0:
        boss_commands.add_chat(message)


@BOT.message_handler(commands=['del_chat'])
@LOG.wrap
def del_chat_handler(message):
    """Removes chat from the system."""
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.del_chat(message)


@BOT.message_handler(commands=['admin_place'])
@LOG.wrap
def add_admin_place_handler(message):
    """Add admin place to system"""
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.add_admin_place(message)


@BOT.message_handler(commands=['money_on', 'money_off'])
@LOG.wrap
def money_mode_change_handler(message):
    """ Enable or disable money system """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.money_mode_change(message)


@BOT.message_handler(commands=['money_reset'])
@LOG.wrap
def money_reset_handler(message):
    """Take all users' money to a system fund"""
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.money_reset(message)


@BOT.message_handler(commands=['m_emoji'])
@LOG.wrap
def money_emoji_handler(message):
    """ Put emoji to indicate the amount of currency """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.money_emoji(message)


@BOT.message_handler(commands=['m_name'])
@LOG.wrap
def money_name_handler(message):
    """ Set currency name """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.set_money_name(message)


@BOT.message_handler(commands=config_var.FEATURES_OFFERS + config_var.FEATURES_ONERS +
                     config_var.FEATURES_DEFAULTERS)
@LOG.wrap
def chat_options_handler(message):
    """ Change chat options """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.chat_options(message)


@BOT.message_handler(commands=['standard_greetings'])
@LOG.wrap
def update_standard_greetings_handler(message):
    """ Change standard greeting """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.update_greetings_json(message, 'standard')


@BOT.message_handler(commands=['captcha_greetings'])
@LOG.wrap
def update_captcha_greetings_handler(message):
    """ Change captcha greeting """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.update_greetings_json(message, 'captcha')


@BOT.message_handler(commands=['admin_greetings'])
@LOG.wrap
def update_admin_greetings_handler(message):
    """ Change admin's greeting """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.update_greetings_json(message, 'admin')


@BOT.message_handler(commands=['full_admin_greetings'])
@LOG.wrap
def update_full_admin_greetings_handler(message):
    """ Change full admin's greeting """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.update_greetings_json(message, 'full_admin')


@BOT.message_handler(commands=config_var.SYSTEM_FEATURES_ONERS + config_var.SYSTEM_FEATURES_OFFERS)
@LOG.wrap
def system_options_handler(message):
    """ Change chat system options """
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "chat_changer"):
        boss_commands.system_options(message)


# Составные команды


@BOT.callback_query_handler(func=lambda call: call.data == 'captcha')
@LOG.wrap
def captcha_completed_handler(call):
    """ It is executing when new member passes the captcha """
    complicated_commands.captcha_completed(call)


@BOT.callback_query_handler(func=lambda call: call.data == 'captcha_fail')
@LOG.wrap
def captcha_failed_handler(call):
    """ It is executing when new member fails the captcha """
    complicated_commands.captcha_failed(call)


@BOT.callback_query_handler(func=lambda call: 'adequate' in call.data and call.data != 'inadequate')
@LOG.wrap
def adequate_handler(call):
    """Вариант адекватен"""
    complicated_commands.adequate(call)


@BOT.callback_query_handler(func=lambda call: call.data == 'inadequate')
@LOG.wrap
def inadequate_handler(call):
    """Вариант неадекватен"""
    complicated_commands.inadequate(call)


@BOT.callback_query_handler(func=lambda call: call.data == "new_chat")
@LOG.wrap
def create_new_chat_handler(call):
    """Add new system of chats"""
    member = output.get_member(call.message.chat.id, call.from_user.id)
    if member.status in ("creator", "administrator"):
        complicated_commands.create_new_chat(call)
    else:
        output.answer_callback(call.id, "Для жмака нужно иметь админку")


@BOT.callback_query_handler(func=lambda call: call.data == "part_of_other_chat")
def message_about_add_chat_handler(call):
    """Tell users to use /add_chat x"""
    if output.get_member(call.message.chat.id, call.from_user.id).status in \
            ("creator", "administrator"):
        output.edit_text("Введите команду\n\n/add_chat x\n\n"
                         "Где x это номер системы вашего чата (ищите его в /help вашего чата",
                         call.message.chat.id, call.message.message_id)
    else:
        output.answer_callback(call.id, "Для жмака нужно иметь админку")


@BOT.inline_handler(lambda query: query.query == 'test')
@LOG.wrap
def response_handler(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    complicated_commands.response(inline_query)


@BOT.message_handler(regexp='Признаю оскорблением')
@LOG.wrap
def insult_handler(message):
    """Спращивает, иронично ли признание оскорблением"""
    if config_func.in_mf(message, command_type=None, or_private=False) and config_func.is_suitable(
            message, message.from_user, "standard"):
        complicated_commands.insult(message)


@BOT.callback_query_handler(func=lambda call: call.data == 'non_ironic'
                            )  # триггерится, когда нажата кнопка "Нет"
@LOG.wrap
def non_ironic_handler(call):
    """Реакция, если обвинение было неироничным"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        complicated_commands.non_ironic(call)
    else:
        output.answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.callback_query_handler(func=lambda call: call.data == 'ironic'
                            )  # триггерится, когда нажата кнопка "Да"
@LOG.wrap
def ironic_handler(call):
    """Реакция, если обвинение было ироничным"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        complicated_commands.ironic(call)
    else:
        output.answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.message_handler(commands=['vote', 'multi_vote', 'adapt_vote'])
@LOG.wrap
def vote_handler(message):
    """Генерирует голосовашку"""
    if config_func.in_mf(message, command_type=None, or_private=False):
        complicated_commands.vote(message)


@BOT.callback_query_handler(func=lambda call: 'here' in call.data or 'nedostream' in call.data)
@LOG.wrap
def place_here_handler(call):
    """Выбирает, куда прислать голосовашку"""
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        complicated_commands.place_here(call)
    else:
        output.answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.callback_query_handler(func=lambda call: 'mv_' in call.data)
@LOG.wrap
def mv_handler(call):
    """Обновляет мульти-голосовашку"""
    if call.chat_instance != "-8294084429973252853" or config_func.is_suitable(
            call, call.from_user, "advanced"):
        complicated_commands.multi_vote(call)


@BOT.callback_query_handler(func=lambda call: 'av_' in call.data)
@LOG.wrap
def av_handler(call):
    """Обновляет адапт-голосовашку"""
    if call.chat_instance != "-8294084429973252853" or config_func.is_suitable(
            call, call.from_user, "advanced"):
        complicated_commands.adapt_vote(call)


@BOT.callback_query_handler(
    func=lambda call: call.data == 'favor' or call.data == 'against' or call.data == 'abstain')
@LOG.wrap
def add_vote_handler(call):
    """Вставляет голос в голосоовашку"""
    if call.chat_instance != "-8294084429973252853" or config_func.is_suitable(
            call, call.from_user, "advanced"):
        complicated_commands.add_vote(call)


# Простые команды и старт


@BOT.message_handler(commands=['start'])
@LOG.wrap
def starter_handler(message):
    """Запуск бота в личке, в чате просто реагирует"""
    if config_func.is_correct_message(message) and config_func.in_mf(message, command_type=None):
        starter(message)


@BOT.message_handler(commands=['help'])
@LOG.wrap
def helper_handler(message):
    """Предоставляет человеку список команд"""
    if config_func.is_correct_message(message) and config_func.in_mf(message, command_type=None):
        standard_commands.helper(message)


@BOT.message_handler(commands=['money_help', 'help_money'])
@LOG.wrap
def money_helper_handler(message):
    """Financial instructions"""
    if config_func.in_mf(message, command_type=None):
        standard_commands.money_helper(message)


@BOT.message_handler(commands=['storages'])
@LOG.wrap
def send_list_of_storages_handler(message):
    """ Sends list of all storages """
    if config_func.in_mf(message, command_type=None):
        standard_commands.send_list_of_storages(message)


@BOT.message_handler(commands=['id'])
@LOG.wrap
def show_id_handler(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    if config_func.in_mf(message, command_type=None):
        developer_commands.show_id(message)


@BOT.message_handler(commands=['echo'])
@LOG.wrap
def echo_message_handler(message):
    """ Repeats message """
    if config_func.in_mf(message, command_type=None):
        developer_commands.echo_message(message)


@BOT.message_handler(commands=['clear'])
@LOG.wrap
def clear_echo_message_handler(message):
    """ Clears echo messages """
    if config_func.in_mf(message, command_type=None):
        developer_commands.clear_echo_message(message)


@BOT.message_handler(commands=['html'])
@LOG.wrap
def html_echo_message_handler(message):
    """ Repeats message with HTML message markup """
    if config_func.in_mf(message, command_type=None):
        developer_commands.html_echo_message(message)


@BOT.message_handler(commands=['rights'])
@LOG.wrap
def rights_handler(message):
    """ Check bot rights """
    if config_func.in_mf(message, command_type=None):
        developer_commands.get_bot_rights(message)


@BOT.message_handler(commands=['dick_punch'])
@LOG.wrap
def dick_cheek_punch_handler(message):
    """For punching someone's cheek with your dick"""
    if config_func.is_correct_message(message) and config_func.in_mf(message, 'standard_commands'):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person(to_self=True)
        standard_commands.dick_cheek_punch(message, person)


@BOT.message_handler(commands=['hug'])
@LOG.wrap
def hug_handler(message):
    """For hugs"""
    if config_func.is_correct_message(message) and config_func.in_mf(message, 'standard_commands'):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person(to_self=True)
        standard_commands.hug(message, person)


@BOT.message_handler(commands=['minet', 'french_style_sex', 'blowjob'])
@LOG.wrap
def minet_handler(message):
    """Приносит удовольствие"""
    if config_func.is_correct_message(message) and config_func.in_mf(message, 'standard_commands'):
        language = config_func.get_one_language(message)
        if language and config_func.cooldown(message, 'minet'):
            standard_commands.minet(message, language)


@BOT.message_handler(commands=['shuffle'])
@LOG.wrap
def shuffle_handler(message):
    """ Shuffle a list """
    if config_func.in_mf(message, 'standard_commands'):
        analyzer = config_func.Analyzer(message, value_necessary=False)
        elements = analyzer.parameters_dictionary['comment'].split()
        if not elements:
            output.reply(message, 'Пожалуйста, напишите список, '
                                  'а элементы списка разделите пробелом')
        shuffle(elements)
        if 'value' in analyzer.parameters_dictionary:
            elements = elements[:analyzer.parameters_dictionary['value']]
        out = '\n'.join(f'{i + 1}. {j}' for i, j in enumerate(elements))
        output.reply(message, out)


@BOT.message_handler(commands=['get'])
@LOG.wrap
def send_stuff_from_storage_handler(message):
    """Send random media from the storage"""
    analyzer = config_func.Analyzer(message, value_necessary=False)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, 'standard_commands') and config_func.check_access_to_a_storage(
            message, storage_name, False) and config_func.cooldown(message, storage_name,
                                                                   timeout=300):
        if "value" in analyzer.parameters_dictionary:
            stuff_number = analyzer.parameters_dictionary["value"]
            standard_commands.send_numbered_stuff_from_storage(message, storage_name, stuff_number)
        else:
            standard_commands.send_random_stuff_from_storage(message, storage_name)


@BOT.message_handler(commands=['size'])
@LOG.wrap
def check_storage_size_handler(message):
    """ Checks how many moderators and how much media there is in a storage """
    analyzer = config_func.Analyzer(message, value_necessary=False)
    storage_name = analyzer.parameters_dictionary['comment']
    if config_func.in_mf(message, 'standard_commands') and config_func.check_access_to_a_storage(
            message, storage_name, False, to_check_vulgarity=False):
        standard_commands.check_storage_size(message, storage_name)


@BOT.message_handler(regexp='есть один мем')
@BOT.message_handler(commands=['meme'])
@LOG.wrap
def send_meme_handler(message):
    """Присылает мем"""
    if config_func.in_mf(message, 'standard_commands') and config_func.cooldown(message, 'meme'):
        standard_commands.send_meme(message)


@BOT.message_handler(commands=['me', 'check', 'check_me', 'check_ebalo'])
@LOG.wrap
def send_me_handler(message):
    """Присылает человеку его запись в БД"""
    if config_func.in_mf(message, command_type=None, or_private=False):
        person = config_func.Analyzer(message,
                                      value_necessary=False).return_target_person(to_self=True)
        if person:
            standard_commands.send_me(message, person)


@BOT.message_handler(commands=['members'])
@LOG.wrap
def all_members_handler(message):
    """Присылает человеку все записи в БД"""
    if config_func.in_mf(message, command_type=None, or_private=False):
        language = config_func.get_one_language(message)
        if language:
            if config_func.is_suitable(message, message.from_user, 'boss', loud=False):
                standard_commands.send_some_top(message, language,
                                                '{index}. <code>{id}</code> {p_link}\n')
            else:
                standard_commands.send_some_top(message, language,
                                                '{index}. <code>{id}</code> {nickname}\n')


@BOT.message_handler(commands=['give'])
@LOG.wrap
def money_give_handler(message):
    """Обмен денег между пользователями"""
    if config_func.in_mf(message, 'financial_commands', or_private=False):
        analyzer = config_func.Analyzer(message)
        person = analyzer.return_target_person()
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            standard_commands.money_give(message, person, parameters_dictionary)


@BOT.message_handler(commands=['fund'])
@LOG.wrap
def money_fund_handler(message):
    """Transfer money to the chat fund"""
    if config_func.in_mf(message, 'financial_commands', or_private=False):
        analyzer = config_func.Analyzer(message)
        parameters_dictionary = analyzer.parameters_dictionary
        if parameters_dictionary:
            standard_commands.money_fund(message, parameters_dictionary)


@BOT.message_handler(commands=['top', 'money_top'])
@LOG.wrap
def money_top_handler(message):
    """Топ ЯМ"""
    if config_func.in_mf(message, 'financial_commands', or_private=False):
        language = config_func.get_one_language(message)
        if language:
            args = message, language, '{index}. {p_link} — {money} {m_emo}\n'
            kwargs = {'start': 'Бюджет: {bot_money} {m_emo}\n\n', 'sort_key': lambda x: x['money']}
            if config_func.is_suitable(message, message.from_user, 'boss', loud=False):
                standard_commands.send_some_top(*args, **kwargs)
            else:
                standard_commands.send_short_top(*args, **kwargs)


@BOT.message_handler(commands=['warns'])
@LOG.wrap
def warns_top_handler(message):
    """ Show all warns """
    if config_func.in_mf(message, command_type=None, or_private=False):
        language = config_func.get_one_language(message)
        if language:
            args = message, language, '{index}. {p_link} — {warns} ⛔️\n'
            kwargs = {'start': 'Количество варнов:\n\n', 'sort_key': lambda x: x['warns']}
            standard_commands.send_some_top(*args, **kwargs)


@BOT.message_handler(commands=['messages_top'])
@LOG.wrap
def messages_top_handler(message):
    """Messages top"""
    if config_func.in_mf(message, command_type=None, or_private=False):
        language = config_func.get_one_language(message)
        if language:
            args = message, language, '{index}. {p_link} — {messages} сообщ.\n'
            kwargs = {'sort_key': lambda x: x['messages']}
            if config_func.is_suitable(message, message.from_user, 'boss', loud=False):
                standard_commands.send_some_top(*args, **kwargs)
            else:
                standard_commands.send_short_top(*args, **kwargs)


@BOT.message_handler(commands=['month'])
@LOG.wrap
def month_set_handler(message):
    """Set month of person's birthday"""
    if config_func.in_mf(message, command_type=None):
        month = message.text.split()[-1]
        if month.isdecimal():
            month = int(month)
            if month and 1 <= month <= 12:
                standard_commands.month_set(message, month)
        else:
            output.reply(
                message, "Последнее слово должно быть положительным числом от 1 до 12 — "
                         "номером месяца")


@BOT.message_handler(commands=['day'])
@LOG.wrap
def day_set_handler(message):
    """Set day of person's birthday"""
    if config_func.in_mf(message, command_type=None):
        day = message.text.split()[-1]
        if day.isdecimal():
            day = int(day)
            if day and 1 <= day <= 31:
                language = config_func.get_one_language(message)
                if language:
                    standard_commands.day_set(message, day, language)
        else:
            output.reply(
                message, "Последнее слово должно быть положительным числом от 1 до 31 — "
                         "номером дня")


@BOT.message_handler(commands=['bdays', 'birthdays'])
@LOG.wrap
def birthday_handler(message):
    """Show the nearest birthdays"""
    if config_func.in_mf(message, command_type=None):
        language = config_func.get_one_language(message)
        if language:
            standard_commands.send_some_top(
                message,
                language,
                '{index}. {p_link} — {day} {month}\n',
                sort_key=lambda x: -100 * x['month_birthday'] - x['day_birthday'])


@BOT.message_handler(commands=['admins', 'report'])
@LOG.wrap
def admins_handler(message):
    """Ping admins"""
    if config_func.in_mf(message, command_type=None) and config_func.is_suitable(message,
                                                                                 message.from_user,
                                                                                 "standard") \
            and config_func.cooldown(message, 'admins', 300):
        standard_commands.admins(message)


@BOT.message_handler(commands=['chat'])
@LOG.wrap
def chat_check_handler(message):
    """Show options of the current chat"""
    if config_func.in_mf(message, command_type=None, or_private=False):
        standard_commands.chat_check(message)


@BOT.message_handler(commands=['system'])
@LOG.wrap
def system_check_handler(message):
    """Show options of the current chat"""
    if config_func.in_mf(message, command_type=None, or_private=False):
        standard_commands.system_check(message)


@BOT.message_handler(commands=['anon'])
@LOG.wrap
def anon_message_handler(message):
    """Send anon message to admin place"""
    if message.chat.id > 0:
        if len(message.text) == 5:
            output.reply(message,
                         "После команды /anon должно следовать то, что надо отправить админам")
        else:
            standard_commands.anon_message(message)
    else:
        output.reply(message, "Эта команда предназначена для лички")


@BOT.message_handler(commands=['test'])
@LOG.wrap
def database_send_handler(message):
    """ Send all databases to config_var.CREATOR_ID """
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
@LOG.wrap
def counter_handler(message):
    """Подсчитывает сообщения"""
    if config_func.in_mf(message, command_type=None, loud=False, or_private=False):
        reactions.trigger(message)
