# -*- coding: utf-8 -*-
"""This is config functions. They are pretty important part of the bot
so don't mess with them
"""
import json
import time
from threading import Thread
from random import shuffle
from ast import literal_eval
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from presenter.config.config_var import BOT_ID, NEW_SYSTEM_JSON_ENTRY,\
    ADD_CHAT_KEYBOARD, ENTITIES_TO_PARSE
from presenter.config.database_lib import Database
from presenter.config.files_paths import ADAPT_VOTES_FILE, MULTI_VOTES_FILE, VOTES_FILE, \
    SYSTEMS_FILE, STORAGE_FILE
from presenter.config.log import Logger
from view.output import reply, kick, answer_callback, edit_text, edit_markup, get_member, \
    unban, get_chat, get_me


LOG = Logger()


class Captchers:
    """List of people completing the captcha"""

    def __init__(self):
        self.list = []

    def remove_captcher(self, user_id, chat_id):
        """Remove the user from CAPTCHERS list"""
        if (user_id, chat_id) in self.list:
            self.list.remove((user_id, chat_id))
            return True
        return False

    def remove(self, element):
        """Remove an element from a list"""
        self.list.remove(element)

    def append(self, element):
        """Append an element to a list"""
        self.list.append(element)


CAPTCHERS = Captchers()


class CaptchaBan(Thread):
    """Waits for person to complete the captcha. Bans them if time is up."""

    def __init__(self, message, bots_message):
        Thread.__init__(self)
        LOG.log("CaptchaBan invoked")
        self.message = message
        self.bots_message = bots_message

    def run(self):
        CAPTCHERS.append((self.message.new_chat_members[0].id, self.message.chat.id))
        time.sleep(300)
        if (self.message.new_chat_members[0].id, self.message.chat.id) in CAPTCHERS.list:
            kick_and_unban(self.message.chat.id, self.message.new_chat_members[0].id)
            edit_text("Испытание креветкой провалено! (время истекло)", self.bots_message.chat.id,
                      self.bots_message.message_id)
            CAPTCHERS.remove((self.message.new_chat_members[0].id, self.message.chat.id))


class SystemUpdate(Thread):
    """Updates all entries in some system"""

    def __init__(self, chat_id, system_id, members, sent):
        Thread.__init__(self)
        LOG.log("SystemUpdate invoked")
        self.chat_id = chat_id
        self.system_id = system_id
        self.members = members
        self.sent = sent

    def run(self):
        for member in self.members:
            user = get_member(self.chat_id, member['id'])
            if user:
                member_update(self.system_id, user.user)
        reply(self.sent, "Теперь записи о людях максимально свежие!")


class WaitAndUnban(Thread):
    """Some timer passes some time and user if unbanned"""

    def __init__(self, chat_id, user_id):
        Thread.__init__(self)
        LOG.log("WaitAndUnban invoked")
        self.chat_id = chat_id
        self.user_id = user_id

    def run(self):
        time.sleep(3)
        unban(self.chat_id, self.user_id)


def kick_and_unban(chat_id, user_id):
    """Kicks user and unbans them immediately"""
    kick(chat_id, user_id)
    wait_and_unban = WaitAndUnban(chat_id, user_id)
    wait_and_unban.start()


def get_text_and_entities(target_message):
    """Get text and entities from the message"""
    if target_message.text:
        text = target_message.text
        entities = target_message.entities
    else:
        text = target_message.caption
        entities = target_message.caption_entities
    return text, entities


def entities_saver(text, entities):
    """Copies the text and saves all the entities"""
    points = set()
    entities_blocks = []
    if entities and ({e.type for e in entities}.intersection(ENTITIES_TO_PARSE)):
        for entity in entities:
            if entity.type in ('bold', 'italic', 'underline', 'strikethrough', 'code'):
                points.add(entity.offset)
                points.add(entity.offset + entity.length)
                entities_blocks.append((entity.offset, entity.offset + entity.length, entity.type))
            elif entity.type == 'text_link':
                points.add(entity.offset)
                points.add(entity.offset + entity.length)
                entities_blocks.append((entity.offset, entity.offset + entity.length,
                                        entity.type, entity.url))
        points = list(points)
        points.sort()
        start_text = text[:points[0]]
        end_text = text[points[-1]:]
        points_blocks = []
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            points_blocks.append([start, end, html_cleaner(text[start:end])])
        for point_block in points_blocks:
            for entity_block in entities_blocks:
                if entity_block[0] <= point_block[0] and point_block[1] <= entity_block[1]:
                    if entity_block[2] == 'code':
                        point_block[2] = "<code>" + point_block[2] + "</code>"
                    elif entity_block[2] == 'text_link':
                        point_block[2] = f'<a href="{entity_block[3]}">{point_block[2]}</a>'
                    else:
                        letter = entity_block[2][0]
                        point_block[2] = f"<{letter}>{point_block[2]}</{letter}>"
        text_blocks = [point_block[2] for point_block in points_blocks]
        return start_text + ''.join(text_blocks) + end_text
    return html_cleaner(text)


def html_cleaner(text: str) -> str:
    """Cleans html-entities irrelevant for some reason"""
    if text:
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return ''


def get_target_message(message):
    """Returns message that was replied to or current message if it's not a reply"""
    reply_to = message.reply_to_message
    if reply_to:
        return reply_to
    return message


def create_captcha_keyboard():
    """Creates 5x5 buttons keyboard with animals as a captcha

    :return InlineKeyboardMarkup
    """
    wrong_animals_string = '🦀🦞🦑🐡🐶🐱🐭🐹🐰🦊🐻🐼🐵🐸🐷🐮🦁🐯🐨🙈🙉🙊🐒🐔🐧🐦🐤🐗🐺🦇🦉🦅🦆🐥🐣🐴🦄'
    wrong_animals_string += '🐝🐛🦋🐌🐞🐜🦎🐍🐢🦂🕷🦗🦟🐆🦓🦍🐘🦛🦏🐪🐫🐏🐖🐎🦔🐈'
    wrong_animals_buttons = []
    for wrong_animal in wrong_animals_string[:24]:
        wrong_animals_buttons.append(InlineKeyboardButton(wrong_animal,
                                                          callback_data="captcha_fail"))
    buttons = [InlineKeyboardButton("🦐", callback_data="captcha")] + wrong_animals_buttons
    shuffle(buttons)
    buttons_rows = list([buttons[i:i + 5] for i in range(0, len(buttons), 5)])
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 5
    for buttons_row in buttons_rows:
        keyboard.add(*buttons_row)
    return keyboard


def remove_slash_and_bot_mention(command: str) -> str:
    """Convert command about adding something to storage into content name

    :param command: like '/some_cool_command@MultiFandomRuBot' or '/some_command blah blah blah'
    :type command: str

    :return: name of the command 'some_cool_command'
    :rtype: str
    """
    command = command.split()[0]  # '/some_command blah blah blah' -> '/some_command'
    command = command.split(sep='@')[0]  # /art_add@MultiFandomRuBot -> /art_add
    command = command[1:]  # /art_add -> art_add
    return command


def person_info_in_html(user) -> str:
    """Converts information about user to pretty string

    :param user
    :type user: User

    :returns: string like 'link_to a person (@username) [id]'
    :rtype: str
    """
    name = html_cleaner(user.first_name)
    id_link = id_link_text_wrapper(name, user.id)
    return f'{id_link} (@{user.username}), [{code_text_wrapper(user.id)}]'


def chat_info_in_html(chat) -> str:
    """

    :param chat:
    :return: string with pretty chat info like 'Multi Fandom 2 (@MultiFandomRu) [-1001408293838]'
    :rtype: str
    """
    return f'{html_cleaner(chat.title)} (@{chat.username}) [{code_text_wrapper(chat.id)}]'


def code_text_wrapper(text):
    """Simply wraps some text into code html-wrap."""
    return f'<code>{text}</code>'


def id_link_text_wrapper(text, person_id):
    """Simply wraps some text into id_link html-wrap."""
    return f'<a href="tg://user?id={person_id}">{text}</a>'


def link_text_wrapper(text, url):
    """Simply wraps some text into url-link html-wrap."""
    return f'<a href="{url}">{text}</a>'


def person_link(person) -> str:
    """Creates a link to a person"""
    if person.username:
        return link_text_wrapper(person.first_name, 't.me/'+person.username)
    return id_link_text_wrapper(person.first_name, person.id)


def value_marker(value: object, normal: str, void: str) -> str:
    """
    Replace an object with a string, depending on the value being incremented (True or False)
    :param value: Value to replace with string
    :param normal: String if value returns True
    :param void: String if value returns False
    :return: Replaced object
    """
    return normal if value else void


def photo_video_gif_get(target_message):
    """Gets the media from the target message to save into a storage"""
    text, entities = get_text_and_entities(target_message)
    final_text = entities_saver(text, entities)
    if target_message.photo:
        return target_message.photo[0].file_id, 'photo', final_text
    if target_message.video:
        return target_message.video.file_id, 'video', final_text
    if target_message.document:
        return target_message.document.file_id, 'gif', final_text
    return None


@LOG.wrap
def get_one_language(message):
    """Analyzes the language that is suitable for some situation"""
    database = Database()
    entry = database.get('languages', ('id', message.chat.id))
    if entry:
        return entry['language']
    reply(message, "Если вы говорите на русском, напишите '/lang Русский'\n\n"
                   "If you speak English, type '/lang English'\n\n")
    return ''


@LOG.wrap
def get_languages(message):
    """Gets all languages that are possibly spoken by user
    :param message: message
    :return dictionary {"Russian": bool, "English": bool}
    :rtype dict"""
    database = Database()
    entry = database.get('languages', ('id', message.chat.id))
    languages = {"Russian": False, "English": False}
    if entry:
        languages[entry['language']] = True
        return languages
    russian = set("ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ")
    english = set("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
    text = message.text
    # filling the variable text chat title, description etc.
    if message.chat.id > 0:
        user = message.from_user
        text += user.first_name
        if user.last_name:
            text += user.last_name
    else:
        chat = get_chat(message.chat.id)
        if chat.title:
            text += chat.title
        if chat.description:
            text += chat.description
    text = set(text)
    languages['Russian'] = bool(russian & text) or (message.from_user.language_code == 'ru')
    languages['English'] = bool(english & text) or (message.from_user.language_code == 'en')
    return languages


def left_new_or_else_member(target_message):
    """Get the target person in leave/entering messages"""
    if target_message.new_chat_members:
        return target_message.new_chat_members[0]
    if target_message.left_chat_member:
        return target_message.left_chat_member
    return target_message.from_user


class Analyzer:
    """Class to get target_person and other parameters"""

    def __init__(self, message, value_necessary=True, default_value=None, value_positive=False):
        self.message = message
        self.parameters_dictionary = parameters_analyze(message.text,
                                                        value_necessary=value_necessary,
                                                        default_value=default_value,
                                                        value_positive=value_positive)
        self.value_positive = value_positive
        if not self.parameters_dictionary:
            str_value_positive = 'ПОЛОЖИТЕЛЬНОЕ' if self.value_positive else ''
            reply(self.message, "Пожалуйста, введите {} ".format(str_value_positive) +
                  "число-значение, необходимое для команды, например\n\n"
                  "/cmd 866828593 50 Комментарий\n\nили\n\n"
                  "[Ответ на сообщение]\n/cmd 50 Комментарий\n\n"
                  "Вы даже можете перемешивать параметры\n\n"
                  "/cmd Комментарий 50 866828593\n"
                  "/cmd 50 Комментарий 866828593\n"
                  "/cmd 866828593 Комментарий 50\n")

    def return_target_person(self, to_self=False, to_bot=False):
        """Get and check target person"""
        target_person = self.get_person(self.parameters_dictionary)
        if self.check_person(target_person, to_self, to_bot):
            return target_person
        return None

    def get_person(self, parameters_dictionary: dict):
        """Gets possible target person"""
        if 'person_id' in parameters_dictionary.keys():
            return get_member(-1001268084945, parameters_dictionary['person_id']).user
        if self.message.reply_to_message:  # Сообщение является ответом
            return left_new_or_else_member(self.message.reply_to_message)
        return self.message.from_user

    @LOG.wrap
    def check_person(self, person, to_self, to_bot):
        """Checks if target person is chosen correctly"""
        if person.id == self.message.from_user.id and not to_self and self.parameters_dictionary:
            reply(
                self.message, "Пожалуйста, введите ID нужного человека (можно найти в /members) "
                              "или ответьте командой на его сообщение\n\n"
                              "Этой командой нельзя пользоваться на себе, "
                              "так что ввести свой же ID или ответить "
                              "на своё же сообщение не выйдет)")
            return False
        if person.id == BOT_ID and not to_bot:
            reply(self.message, "Этой командой нельзя пользоваться на мне")
            return False
        return True


def is_integer(string: str):
    """Returns true if string can be converted into integer and false if it can't"""
    return string.isdigit() or (string[0] == '-' and string[1:].isdigit())


def parameters_analyze(text: str,
                       value_necessary=True,
                       default_value=None,
                       value_positive=False) -> dict:
    """
    :param text: text of user's message
    :type text: str

    :param value_necessary: if it's necessary to return dictionary_of_parameters['value']

    :param default_value: default dictionary_of_parameters['value']

    :param value_positive: if dictionary_of_parameters['value'] must be positive
    :type value_positive: bool

    :return: parameters required for some command
    :rtype: dict
    """
    dictionary_of_parameters = {'command': remove_slash_and_bot_mention(text)}
    if default_value is not None:
        dictionary_of_parameters['value'] = default_value
    parts_of_the_message = text.split()[1:]
    for part in parts_of_the_message:
        if is_integer(part) and get_member(-1001268084945, int(part)):
            dictionary_of_parameters['person_id'] = int(part)
            parts_of_the_message.remove(part)
            break
    for part in parts_of_the_message:
        if is_integer(part):
            dictionary_of_parameters['value'] = int(part)
            parts_of_the_message.remove(part)
            break
    dictionary_of_parameters['comment'] = ' '.join(parts_of_the_message)
    if not value_necessary or ('value' in dictionary_of_parameters.keys() and
                               (dictionary_of_parameters['value'] > 0 or not value_positive)):
        return dictionary_of_parameters
    return dict()


@LOG.wrap
def rank_superiority(message, person):
    """Checks if user's rank is superior to person's rank"""
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    chat_configs = get_system_configs(system)
    ranks = chat_configs['ranks']

    your_rank = database.get('members', ('id', message.from_user.id), ('system', system))['rank']
    your_rank_n = ranks.index(your_rank)

    person_entry = get_person(message, person, system, database, system_configs=chat_configs)
    their_rank = person_entry['rank']
    their_rank_n = ranks.index(their_rank)

    if your_rank_n < their_rank_n:
        text = f"Для этого ваше звание ({your_rank}) должно превосходить звание цели ({their_rank})"
        reply(message, text)
    return your_rank_n > their_rank_n


def add_person(message, person, system, database, system_configs):
    """Add entry to database about some person in some system"""
    chat_member_status = get_member(message.chat.id, person.id).status
    boss_commands_requirements = system_configs["commands"]["boss"]
    if chat_member_status == "creator":
        rank = system_configs['ranks'][-1]
    elif chat_member_status == 'administrator' and isinstance(boss_commands_requirements, list):
        rank = boss_commands_requirements[0]  # minimal rank to use admin commands
    else:
        rank = system_configs['ranks'][1]
    person_entry = (person.id, system, person.username, person.first_name,
                    rank, 0, 0, 0, 0, 0)
    database.append(person_entry, 'members')


def get_person(message, person, system: str, database: Database, system_configs=None) -> dict:
    """Get entry about some person in some system, create if there wasn't"""
    person_entry = database.get('members', ('id', person.id), ('system', system))
    if not person_entry:
        if not system_configs:
            system_configs = get_system_configs(system)
        add_person(message, person, system, database, system_configs)
        person_entry = database.get('members', ('id', person.id), ('system', system))
    return person_entry


def rank_required(message, person, system, min_rank, loud=True):
    """Checks if person has rank required for something"""
    LOG.log("rank_required invoked from userID {}".format(message.from_user.id))
    database = Database()
    chat_configs = get_system_configs(system)
    ranks = chat_configs['ranks']
    you = get_person(message, person, system, database, system_configs=chat_configs)
    your_rank = you['rank']
    your_rank_n = ranks.index(your_rank)
    min_rank_n = ranks.index(min_rank)
    if your_rank_n < min_rank_n and loud:
        if isinstance(message, CallbackQuery):
            answer_callback(message.id,
                            "Ваше звание ({}) не дотягивает до звания ({}) для жмака".format(
                                your_rank, min_rank),
                            show_alert=True)
        else:
            reply(
                message, "Ваше звание ({}) не дотягивает до необходимого ({}) для этого".format(
                    your_rank, min_rank))
    return min_rank_n <= your_rank_n


@LOG.wrap
def appointment_required(message, person, system, appointment, loud=True):
    """Checks if person has appointment required for something"""
    database = Database()
    true_false = database.get("appointments", ('id', person.id), ('appointment', appointment),
                              ('system', system))
    if not true_false and loud:
        reply(message, "Вам для этого нужна должность {}".format(appointment))
    return true_false


@LOG.wrap
def is_suitable(inputed, person, command_type, system=None, loud=True):
    """Function to check if this command can be permitted in current chat"""
    database = Database()
    # determine if input is a message or a callback query
    if isinstance(inputed, CallbackQuery):
        message = inputed.message
    else:
        message = inputed
    # determine which system chat belongs to, and check for requirements
    chat = database.get('chats', ('id', message.chat.id))
    if chat and not system:
        system = chat['system']
    chat_configs = get_system_configs(system)
    requirements = chat_configs['commands'][command_type]
    # check if requirement for this command type is a rank or appointment
    if isinstance(requirements, list):  # Requirement is a list
        return rank_required(inputed, person, system, requirements[0], loud=loud)
    if isinstance(requirements, str):  # Requirement is a string
        return appointment_required(message, person, system, requirements, loud=loud)
    return False


@LOG.wrap
def cooldown(message, command, timeout=3600):
    """Checks if the function is ready to be used again"""
    if message.chat.id > 0:  # Command is used in PM's
        return True
    database = Database()
    # Получаем наименование необходимой команды
    entry = database.get('cooldown', ('person_id', message.from_user.id), ('command', command),
                         ('chat_id', message.chat.id))
    if not entry:  # Чел впервые пользуется коммандой
        database.append((message.from_user.id, command, message.chat.id, message.date), 'cooldown')

        return True
    # Чел уже пользовался командой
    time_passed = message.date - entry['time']
    if time_passed < timeout:  # Кулдаун не прошёл
        seconds = timeout - time_passed
        minutes = seconds // 60
        seconds %= 60
        answer = "Воу, придержи коней, ковбой. Ты сможешь воспользоваться этой командой только "
        answer += f"через {minutes} минут и {seconds} секунд 🤠"
        reply(message, answer)

        return False
    # Кулдаун прошёл
    database.change(message.date, 'time', 'cooldown', ('person_id', message.from_user.id),
                    ('command', command), ('chat_id', message.chat.id))
    return True


def time_replace(seconds):
    """Converts time in GMT+0 into GMT+3 and return days, hours, minutes and seconds"""
    _, _, days, hours, minutes, seconds, *_ = time.gmtime(seconds + 3600 * 3)
    return days, hours, minutes, seconds


def count_message(func):
    def wrapper(message):
        person = left_new_or_else_member(message)
        counter(message, person)  # Отправляем сообщение на учёт в БД
        func(message)
    return wrapper


@LOG.wrap
def in_mf(message, command_type, or_private=True, loud=True):
    """Позволяет регулировать использование команл вне чатов и в личке"""
    if message.chat.id > 0:  # is a private chat
        if loud and not or_private:
            reply(message, "Эта команда отключена в ЛС")
        return or_private

    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    if not chat:
        if loud:
            reply(message, "Доброго времени суток! Перед тем как мной пользоваться, "
                           "ответьте мне на 1 вопрос: "
                           "Этот чат новый или связан с уже существующим чатом?",
                  reply_markup=ADD_CHAT_KEYBOARD)
        return False

    # Начинаем оруэлловщину
    person = left_new_or_else_member(message)
    system = chat['system']
    chat_configs = get_system_configs(system)
    get_person(message, person, system, database, system_configs=chat_configs)
    counter(message, person)
    # Заканчиваем оруэлловщину

    if command_type == 'financial_commands' and not chat_configs['money']:
        reply(message, "В этом чате система денег не включена. Смотрите /money_help")
        return False
    if command_type is None:
        return True
    if feature_is_available(message.chat.id, system, command_type):
        return True
    if loud and not database.get('systems', ('id', system), (command_type, 0)):
        reply(message, "В данном чате команды типа {} не поддерживаются. "
                       "Проверьте /chat".format(command_type))
    return False


def is_correct_message(message):
    """ Checks if a command has been sent to this bot or if the command is not a forward"""
    cmd = message.text.split("@")
    return not message.forward_from and (len(cmd) == 1 or cmd[1] == get_me().username)


@LOG.wrap
def in_system_commands(message):
    """Check if command is available in this system"""
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    if message.text:
        if chat:
            system = chat['system']
            chat_configs = get_system_configs(system)
            command = message.text.split()[0].split(sep='@')[0]
            every = chat_configs["ranks_commands"] + chat_configs["appointment_adders"]
            every += chat_configs["appointment_removers"]
            return command in every
        return message.text.split()[0] in ("/guest", "/admin", "/senior_admin", "/leader")
    return False


@LOG.wrap
def feature_is_available(chat_id, system, command_type):
    """Checks if some feature is available in this system"""
    database = Database()
    command_mode = database.get('chats', ('id', chat_id))[command_type]
    if command_mode == 1:
        return True
    elif command_mode == 2:
        return database.get('systems', ('id', system), (command_type, 2))
    return False


def loud_feature_is_available(message, chat_id, system, command_type):
    """Checks if some feature is available in this system and tells user if it's not"""
    is_available = feature_is_available(chat_id, system, command_type)
    if not is_available:
        reply(message, "В данном чате такие команды не поддерживаются")
    return is_available


def check_access_to_a_storage(message, storage_name, is_write_mode, to_check_vulgarity=True):
    """Checks if some storage can be accessed"""
    database = Database()
    storages_dict = get_storage_json()
    if storage_name in storages_dict.keys():
        storage = storages_dict[storage_name]
        if is_write_mode:
            if message.from_user.id not in storage['moders']:
                reply(message, "У вас отсутствует разрешение добавлять контент в это хранилище :-(")
                return False
            return True
        if message.chat.id > 0:
            return True
        system = database.get('chats', ('id', message.chat.id))['system']
        if to_check_vulgarity and storage['is_vulgar']:
            return loud_feature_is_available(message, message.chat.id, system, 'erotic_commands')
        return loud_feature_is_available(message, message.chat.id, system, 'standard_commands')
    reply(message, "Хранилища '{}' не существует".format(storage_name))
    return False


@LOG.wrap
def counter(message, person):
    """Подсчитывает сообщения, отправленные челом"""
    database = Database()
    if not database.get('messages', ('person_id', person.id), ('chat_id', message.chat.id)):
        database.append((person.id, message.chat.id, 0), 'messages')
    messages = database.get('messages', ('person_id', person.id),
                            ('chat_id', message.chat.id))['messages']
    database.change(messages + 1, 'messages', 'messages', ('person_id', person.id),
                    ('chat_id', message.chat.id))


@LOG.wrap
def member_update(system, person):
    """Updates nickname, username and messages columns in database"""
    database = Database()
    chats_ids = [
        x['id'] for x in database.get_many('chats', ('messages_count', 2), ('system', system))
    ]
    msg_count = 0
    for chat_id in chats_ids:
        if feature_is_available(chat_id, system, 'messages_count'):
            msg_entry = database.get('messages', ('person_id', person.id), ('chat_id', chat_id))
            if msg_entry:
                msg_count += msg_entry['messages']
    database.change(person.username, 'username', 'members', ('id', person.id))
    database.change(person.first_name, 'nickname', 'members', ('id', person.id))
    database.change(msg_count, 'messages', 'members', ('id', person.id), ('system', system))


def get_systems_json():
    """Get info about all the systems"""
    with open(SYSTEMS_FILE, 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


def get_system_configs(system):
    """Get info about one system"""
    return get_systems_json()[system]


def get_list_from_storage(storage):
    """Get some catalogue from the media storage"""
    with open(STORAGE_FILE, 'r', encoding='utf-8') as read_file:
        return json.load(read_file)[storage]


def get_storage_json():
    """Get the media storage"""
    with open(STORAGE_FILE, 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


def write_storage_json(storages_dict):
    """Write info about all the storage into json file"""
    with open(STORAGE_FILE, 'w', encoding='utf-8') as write_file:
        json.dump(storages_dict, write_file, indent=4, ensure_ascii=False)


def write_systems_json(data):
    """Write info about all the systems into json file"""
    with open(SYSTEMS_FILE, 'w', encoding='utf-8') as write_file:
        json.dump(data, write_file, indent=4, ensure_ascii=False)


def update_systems_json(system, set_what, set_where):
    """Changes some data in some system"""
    data = get_systems_json()
    system_configs = data[system]
    system_configs[set_where] = set_what
    data[system] = system_configs
    write_systems_json(data)


def create_system(message, system_id, database):
    """Create entry about some system"""
    system_tuple = (
        system_id,
        0,  # money in the system
        0,  # admin places of the system
        1,  # standard commands
        1,  # erotic commands
        1,  # boss commands
        1,  # financial commands
        0,  # mutual invites
        2,  # messages count
        1,  # violators_ban
        1,  # admins_promote
        1,  # moves delete
        1,  # newbies captched
    )
    database.append(system_tuple, 'systems')
    data = get_systems_json()
    data[system_id] = dict(NEW_SYSTEM_JSON_ENTRY)
    data[system_id]['name'] = message.chat.title
    write_systems_json(data)


def update_old_systems_json():
    """Fills old json entries with missing attributes"""
    data = get_systems_json()
    for system_number in data.keys():
        data[system_number] = update_dictionary(data[system_number], NEW_SYSTEM_JSON_ENTRY)
    write_systems_json(data)


def update_dictionary(current_dictionary: dict, model_dictionary: dict):
    """Update one dictionary"""
    # first we make sure we don't change the original dictionaries
    current_dictionary = dict(current_dictionary)
    model_dictionary = dict(model_dictionary)
    # then we add missing keys
    for key in model_dictionary.keys():
        if key not in current_dictionary.keys():
            current_dictionary[key] = model_dictionary[key]
        elif isinstance(model_dictionary[key], dict):
            if isinstance(current_dictionary[key], dict):
                # update next layer of the dictionary
                current_dictionary[key] = update_dictionary(current_dictionary[key], model_dictionary[key])
            else:
                current_dictionary[key] = model_dictionary[key]
    # finally we delete unnecessary keys
    key_pop = []  # ha ha k-pop reference
    for key in current_dictionary:
        if key not in model_dictionary.keys():
            key_pop.append(key)
        # we don't need to go to the next layer because this function already does it higher
    for key in key_pop:  # if we pop right in previous loop, RunTimeError will be raised
        current_dictionary.pop(key)
    return current_dictionary


def create_chat(message, system_id, chat_type, link, database):
    """Create entry about some chat in some system"""
    chat_tuple = (
        message.chat.id,
        system_id,
        message.chat.title,
        chat_type,
        link,
        2,  # standard commands
        2,  # erotic commands
        2,  # boss commands
        2,  # financial commands
        2,  # mutual invites
        2,  # messages count
        2,  # violators_ban
        2,  # admins_promote
        2,  # moves delete
        2,  # newbies captched
    )
    database.append(chat_tuple, 'chats')


@LOG.wrap
def create_vote(vote_message):
    """Создаёт голосовашку"""
    with open(VOTES_FILE, 'r', encoding='utf-8') as file:
        votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = literal_eval(votes_shelve)
    else:
        votes_shelve = {}

    votes_shelve[vote_message.message_id] = {
        "time": vote_message.date,
        "text": vote_message.text,
        "favor": {},
        "against": {},
        "abstain": {}
    }
    with open(VOTES_FILE, 'w', encoding='utf-8') as file:
        file.write(str(votes_shelve))


@LOG.wrap
def create_multi_vote(vote_message):
    """Создаёт мульти-голосовашку"""
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    with open(MULTI_VOTES_FILE, encoding='utf-8') as file:
        votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = literal_eval(votes_shelve)
    else:
        votes_shelve = {}

    votes_shelve[vote_message.message_id] = {
        "text": vote_message.text,
        "votes": [],
        "keyboard": [],
        "chat": vote_message.chat.id
    }
    with open(MULTI_VOTES_FILE, 'w', encoding='utf-8') as file:
        file.write(str(votes_shelve))
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


@LOG.wrap
def create_adapt_vote(vote_message):
    """Создаёт адапт-голосовашку"""
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_adapt_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    with open(ADAPT_VOTES_FILE, encoding='utf-8') as file:
        votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = literal_eval(votes_shelve)
    else:
        votes_shelve = {}

    votes_shelve[vote_message.message_id] = {
        "text": vote_message.text,
        "votes": [],
        "keyboard": [],
        "chat": vote_message.chat.id
    }
    with open(ADAPT_VOTES_FILE, 'w', encoding='utf-8') as file:
        file.write(str(votes_shelve))
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


@LOG.wrap
def update_multi_vote(vote_id):
    """Обновляет мульти-голосовашку"""
    with open(MULTI_VOTES_FILE, encoding='utf-8') as file:
        votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = literal_eval(votes_shelve)
    else:
        votes_shelve = {}

    votey = dict(votes_shelve[vote_id])
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_option{}'.format(vote_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    for i in votey['keyboard']:
        keyboard.add(InlineKeyboardButton(i, callback_data='mv_' + str(votey['keyboard'].index(i))))
    # Меняем текст голосовашки
    text = votey["text"]
    for i in votey['votes']:
        text += '\n{}: '.format(i[0]) + ', '.join(i[1].values())
    edit_text(text=text, chat_id=votey['chat'], message_id=vote_id,
              reply_markup=keyboard, parse_mode="HTML")


@LOG.wrap
def update_adapt_vote(vote_id):
    """Обновляет адапт голосовашку"""
    with open(ADAPT_VOTES_FILE, encoding='utf-8') as file:
        votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = literal_eval(votes_shelve)
    else:
        votes_shelve = {}

    votey = dict(votes_shelve[vote_id])
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_adapt_option{}'.format(vote_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    for i in votey['keyboard']:
        keyboard.add(InlineKeyboardButton(i, callback_data='av_' + str(votey['keyboard'].index(i))))
    # Меняем текст голосовашки
    text = votey["text"]
    for i in votey['votes']:
        text += '\n{}: '.format(i[0]) + ', '.join(i[1].values())
    edit_text(text=text, chat_id=votey['chat'], message_id=vote_id,
              reply_markup=keyboard, parse_mode="HTML")


@LOG.wrap
def unban_user(person):
    """Remove ban from user"""
    database = Database()
    chats_to_unban = database.get_many('chats', ('violators_ban', 2))
    for chat in chats_to_unban:
        member = get_member(chat['id'], person.id)
        if member and member.status in ('left', 'kicked'):
            unban(chat['id'], person.id)


def get_chat_type_and_chat_link(chat) -> tuple:
    """
    :param chat: chat we are checking
    :return: chat_type (private/public), link (@_)
    :rtype: tuple"""
    chat_type = 'private'
    link = 'None'
    if chat.username:
        chat_type = 'public'
        link = chat.username
    return chat_type, link
