# -*- coding: utf-8 -*-
import json
import time
from threading import Thread

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from presenter.config.config_var import bot_id, new_system_json_entry
from presenter.config.database_lib import Database
from presenter.config.files_paths import adapt_votes_file, multi_votes_file, votes_file, systems_file, storage_file
from presenter.config.log import Loger
from presenter.config.log import log_to
from view.output import *

log = Loger()
captchers = []


class CaptchaBan(Thread):
    def __init__(self, message, bots_message):
        Thread.__init__(self)
        log.log_print("CaptchaBan invoked")
        self.message = message
        self.bots_message = bots_message

    def run(self):
        global captchers
        captchers.append((self.message.new_chat_members[0].id, self.message.chat.id))
        time.sleep(300)
        if (self.message.new_chat_members[0].id, self.message.chat.id) in captchers:
            kick(self.message.chat.id, self.message.new_chat_members[0].id)
            unban(self.message.chat.id, self.message.new_chat_members[0].id)
            edit_text("Испытание креветкой провалено!", self.bots_message.chat.id, self.bots_message.message_id)


class SystemUpdate(Thread):
    def __init__(self, chat_id, system_id, members, sent):
        Thread.__init__(self)
        log.log_print("SystemUpdate invoked")
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


def remove_captcher(call):
    global captchers
    if (call.from_user.id, call.message.chat.id) in captchers:
        captchers.remove((call.from_user.id, call.message.chat.id))
        return True


def get_text_and_entities(target_message):
    if target_message.text:
        text = target_message.text
        entities = target_message.entities
    else:
        text = target_message.caption
        entities = target_message.caption_entities
    return text, entities


def entities_saver(text, entities):
    points = set()
    entities_blocks = []
    if entities and set([e.type for e in entities]) & {'bold', 'italic', 'underline', 'strikethrough', 'code',
                                                       'text_link'}:
        for entity in entities:
            if entity.type in ('bold', 'italic', 'underline', 'strikethrough', 'code'):
                points.add(entity.offset)
                points.add(entity.offset+entity.length)
                entities_blocks.append((entity.offset, entity.offset+entity.length, entity.type))
            elif entity.type == 'text_link':
                points.add(entity.offset)
                points.add(entity.offset + entity.length)
                entities_blocks.append((entity.offset, entity.offset + entity.length, entity.type, entity.url))
        points = list(points)
        points.sort()
        start_text = text[:points[0]]
        end_text = text[points[-1]:]
        points_blocks = []
        for i in range(len(points)-1):
            start = points[i]
            end = points[i+1]
            points_blocks.append([start, end, html_cleaner(text[start:end])])
        for point_block in points_blocks:
            for entity_block in entities_blocks:
                if entity_block[0] <= point_block[0] and point_block[1] <= entity_block[1]:
                    if entity_block[2] == 'bold':
                        point_block[2] = "<b>" + point_block[2] + "</b>"
                    elif entity_block[2] == 'italic':
                        point_block[2] = "<i>" + point_block[2] + "</i>"
                    elif entity_block[2] == 'underline':
                        point_block[2] = "<u>" + point_block[2] + "</u>"
                    elif entity_block[2] == 'strikethrough':
                        point_block[2] = "<s>" + point_block[2] + "</s>"
                    elif entity_block[2] == 'code':
                        point_block[2] = "<code>" + point_block[2] + "</code>"
                    elif entity_block[2] == 'text_link':
                        point_block[2] = f'<a href="{entity_block[3]}">{point_block[2]}</a>'
        text_blocks = [point_block[2] for point_block in points_blocks]
        return start_text + ''.join(text_blocks) + end_text
    else:
        return text


def html_cleaner(text):
    #  < with &lt;, > with &gt; and & with &amp;
    return text.replace('&', '&amp').replace('<', '&lt').replace('>', '&gt')


def photo_video_gif_get(target_message):
    text, entities = get_text_and_entities(target_message)
    final_text = entities_saver(text, entities)
    if target_message.photo:
        return target_message.photo[0].file_id, 'photo', final_text
    elif target_message.video:
        return target_message.video.file_id, 'video', final_text
    elif target_message.document:
        return target_message.document.file_id, 'gif', final_text


def int_check(string, positive):
    if positive:
        if set(string) & set('0123456789') == set(string):
            return int(string)
        else:
            return None
    elif set(string[1:]) & set('0123456789') == set(string[1:]) and string[0] in '-0123456789':
        return int(string)
    else:
        return None


def language_analyzer(message, only_one):
    log.log_print(f"language_analyzer invoked")
    database = Database()
    entry = database.get('languages', ('id', message.chat.id))
    languages = {"Russian": False, "English": False}

    if entry:
        if only_one:
            return entry['language']
        else:
            languages[entry['language']] = True
            return languages
    else:
        russian = set("ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ")
        english = set("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
        text = message.text
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
    languages['Russian'] = bool(russian & text) | (message.from_user.language_code == 'ru')
    languages['English'] = bool(english & text) | (message.from_user.language_code == 'en')
    count = 0
    language_answer = None
    for language in languages.keys():
        if languages[language]:
            count += 1
            language_answer = languages[language]
    if only_one and count == 1:
        return language_answer
    elif only_one:
        answer = ''
        if languages['Russian']:
            answer += "Если вы говорите на русском, напишите '/lang Русский'\n\n"
        if languages['English']:
            answer += "If you speak English, type '/lang English'\n\n"
        reply(message, answer)
        return None
    else:
        return languages


def case_analyzer(word, language):
    if language == 'Russian':
        if word[-1] == 'ь':
            return word[:-1] + 'е'
        else:
            return word + 'е'
    else:
        return word


def person_check(message, person, to_self=False, to_bot=False):
    log.log_print(f"{__name__} invoked")
    if person.id == message.from_user.id and not to_self:
        reply(message, "Этой командой нельзя пользоваться на самом себе")
        return False
    elif person.id == bot_id and not to_bot:
        reply(message, "Этой командой нельзя пользоваться на мне")
        return False
    else:
        return True


def person_analyze(message, to_self=False, to_bot=False):
    log.log_print("person_analyze invoked")
    if message.reply_to_message:  # Сообщение является ответом
        if message.reply_to_message.new_chat_members:
            person = message.reply_to_message.new_chat_members[0]
        else:
            person = message.reply_to_message.from_user
        if person_check(message, person, to_self, to_bot):
            return person
    elif len(message.text.split()) > 1:
        par = message.text.split()[1]
        if int_check(par, positive=True) and 7 <= len(par) <= 10:
            member = get_member(message.chat.id, par)
            if member:
                print(member.status)
                person = member.user
                if person_check(message, person, to_self, to_bot):
                    return person
            else:
                reply(message, "Не вижу такого ID")
        else:
            reply(message, "Некорректный ID. ID это число, которое содержит в себе от 7 до 10 цифр")
    elif to_self:
        return message.from_user
    else:
        reply(message, "Ответьте на сообщение необходимого человека или напишите после команды его ID")


def rank_superiority(message, person):
    log.log_print(f"{__name__} invoked")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    read_file = open(systems_file, 'r', encoding='utf-8')
    data = json.load(read_file)
    read_file.close()
    chat_configs = data[str(system)]
    ranks = chat_configs['ranks']
    your_rank = database.get('members', ('id', message.from_user.id), ('system', system))['rank']
    person_entry = get_person(person, system, database, system_configs=chat_configs)
    their_rank = person_entry['rank']
    your_rank_n = ranks.index(your_rank)
    their_rank_n = ranks.index(their_rank)
    if their_rank_n >= your_rank_n:
        reply(message, "Для этого ваше звание ({}) должно превосходить звание цели ({})".format(your_rank, their_rank))
        return False
    else:
        return True


def add_person(person, system, database, system_configs):
    # TODO ранг зависит от статуса чела, при обнаружении ботом
    person_entry = (person.id, system, person.username, person.first_name, system_configs['ranks'][1], 0, 0, 0, 0, 0)
    database.append(person_entry, 'members')


def get_person(person, system, database, system_configs=None):
    person_entry = database.get('members', ('id', person.id), ('system', system))
    if not person_entry:
        if not system_configs:
            system_configs = get_system_configs(system)
        add_person(person, system, database, system_configs)
        person_entry = database.get('members', ('id', person.id), ('system', system))
    return person_entry


def rank_required(message, person, system, min_rank, max_rank, loud=True):
    log.log_print("rank_required invoked from userID {}".format(message.from_user.id))
    database = Database()
    read_file = open(systems_file, 'r', encoding='utf-8')
    data = json.load(read_file)
    read_file.close()
    chat_configs = data[system]
    ranks = chat_configs['ranks']
    you = get_person(person, system, database, system_configs=chat_configs)
    your_rank = you['rank']
    your_rank_n = ranks.index(your_rank)
    min_rank_n = ranks.index(min_rank)
    max_rank_n = ranks.index(max_rank)
    if your_rank_n < min_rank_n and loud:
        if type(message) == CallbackQuery:
            answer_callback(message.id,
                            "Ваше звание ({}) не дотягивает до звания ({}) для жмака"
                            .format(your_rank, min_rank), show_alert=True)
        else:
            reply(message, "Ваше звание ({}) не дотягивает до необходимого ({}) для данной команды"
                  .format(your_rank, min_rank))
    elif your_rank_n > max_rank_n and loud:
        if type(message) == CallbackQuery:
            answer_callback(message.id,
                            "Ваше звание ({}) выше максимального ({}) для жмака. Гордитесь своим превосходством"
                            .format(your_rank, max_rank), show_alert=True)
        else:
            reply(message, "Ваше звание ({}) выше максимального ({}) для данной команды. Гордитесь своим превосходством"
                  .format(your_rank, max_rank))
    return min_rank_n <= your_rank_n <= max_rank_n


def appointment_required(message, person, system, appointment, loud=True):
    log.log_print("appointment_required invoked")
    database = Database()
    true_false = database.get("appointments", ('id', person.id), ('appointment', appointment),
                              ('system', system))
    if not true_false and loud:
        reply(message, "Вам для этого нужна должность {}".format(appointment))
    return true_false


def is_suitable(inputed, person, command_type, system=None, loud=True):
    """Function to check if this command can be permitted in current chat"""
    log.log_print("is_suitable invoked")
    database = Database()
    # determine if input is a message or a callback query
    if type(inputed) == CallbackQuery:
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
        return rank_required(inputed, person, system, requirements[0], requirements[1], loud=loud)
    elif isinstance(requirements, str):  # Requirement is a string
        return appointment_required(message, person, system, requirements, loud=loud)


def cooldown(message, command, timeout=3600):
    log.log_print("cooldown invoked")
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
    else:  # Кулдаун прошёл
        database.change(message.date, 'time', 'cooldown', ('person_id', message.from_user.id), ('command', command),
                        ('chat_id', message.chat.id))

        return True


def time_replace(seconds):
    _, _, days, hours, minutes, seconds, *_ = time.gmtime(int(time.time()) + 3600*3)
    return days, hours, minutes, seconds


def in_mf(message, command_type, or_private=True, loud=True):
    """Позволяет регулировать использование команл вне чатов и в личке"""
    log.log_print("in_mf invoked")
    database = Database()

    if message.new_chat_members:
        person = message.new_chat_members[0]
    elif message.left_chat_member:
        person = message.left_chat_member
    else:
        person = message.from_user

    if message.chat.id > 0:
        if loud and not or_private:
            person = message.from_user
            send(381279599, "Некто {} ({}) [{}] попыталcя использовать команду {} в личке"
                 .format(person.first_name, person.username, person.id, message.text))
            reply(message, "Эта команда отключена в ЛС")
        return or_private

    chat = database.get('chats', ('id', message.chat.id))
    if chat:
        chat_id = message.chat.id
        system = chat['system']
        chat_configs = get_system_configs(system)
        get_person(person, system, database, system_configs=chat_configs)
        counter(message, person)  # Отправляем сообщение на учёт в БД
        if command_type == 'financial_commands':
            if not chat_configs['money']:
                reply(message, "В этом чате система денег не включена. Смотрите /money_help")
                return False
        if command_type:
            if feature_is_available(chat_id, system, command_type):
                return True
            else:
                if loud and not database.get('systems', ('id', system), (command_type, 0)):
                    reply(message, "В данном чате команды такого типа не поддерживаются")
                return False
        else:
            return True
    if loud:
        text = "Люди из чата с ID {} и названием {}, в частности {} (@{}) [{}] "
        text += "попытались мной воспользоваться"
        send(381279599, text.format(message.chat.id, message.chat.title, message.from_user.first_name,
                                    message.from_user.username, message.from_user.id))
        rep_text = ""
        rep_text += "Hmm, I don't know this chat. Call @DeMaximilianster for help\n\n"
        rep_text += "Хмм, я не знаю этот чат. Обратитесь к @DeMaximilianster за помощью\n\n"
        reply(message, rep_text)


def is_correct_message(message):
    """ Checks if a command has been sent to this bot or if the command is not a forwarding """
    cmd = message.text.split("@")
    return not message.forward_from and (len(cmd) == 1 or cmd[1] == bot.get_me().username)


def in_system_commands(message):
    """Check if command is available in this system"""
    log.log_print("in_system_commands invoked")
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
        else:
            return message.text.split()[0] in ("/guest", "/admin", "/senior_admin", "/leader")


def feature_is_available(chat_id, system, command_type):
    log.log_print("command_is_available invoked")
    database = Database()
    if database.get('chats', ('id', chat_id), (command_type, 1)):
        return True
    elif database.get('chats', ('id', chat_id), (command_type, 2)) and database.get('systems', ('id', system),
                                                                                               (command_type, 2)):
        return True
    return False


def counter(message, person):
    """Подсчитывает сообщения, отправленные челом"""
    log.log_print("counter invoked")
    database = Database()
    if not database.get('messages', ('person_id', person.id), ('chat_id', message.chat.id)):
        database.append((person.id, message.chat.id, 0), 'messages')
    value = database.get('messages', ('person_id', person.id), ('chat_id', message.chat.id))['messages'] + 1
    database.change(value, 'messages', 'messages', ('person_id', person.id), ('chat_id', message.chat.id))
    # TODO Добавить время последнего сообщения и элитократические взаимодействия с ним


def member_update(system, person):
    log.log_print('member_update invoked')
    database = Database()
    chats_ids = [x['id'] for x in database.get_many('chats', ('messages_count', 2), ('system', system))]
    msg_count = 0
    for chat_id in chats_ids:
        if feature_is_available(chat_id, system, 'messages_count'):
            msg_entry = database.get('messages', ('person_id', person.id), ('chat_id', chat_id))
            if msg_entry:
                msg_count += msg_entry['messages']
    database.change(person.username, 'username', 'members', ('id', person.id), ('system', system))
    database.change(person.first_name, 'nickname', 'members', ('id', person.id), ('system', system))
    database.change(msg_count, 'messages', 'members', ('id', person.id), ('system', system))


def get_systems_json():
    with open(systems_file, 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


def get_system_configs(system):
    data = get_systems_json()
    return data[system]


def get_list_from_storage(storage):
    with open(storage_file, 'r', encoding='utf-8') as read_file:
        return json.load(read_file)[storage]


def get_storage_json():
    with open(storage_file, 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


def write_storage_json(data):
    with open(storage_file, 'w', encoding='utf-8') as write_file:
        json.dump(data, write_file, indent=4, ensure_ascii=False)


def write_systems_json(data):
    with open(systems_file, 'w', encoding='utf-8') as write_file:
        json.dump(data, write_file, indent=4, ensure_ascii=False)


def update_systems_json(system, set_what, set_where):
    data = get_systems_json()
    system_configs = data[system]
    system_configs[set_where] = set_what
    data[system] = system_configs
    write_systems_json(data)


def create_system(message, system_id, database):
    system_tuple = (system_id,
                    0,  # money in the system
                    0,  # admin places of the system
                    1,  # standart commands
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
    data[system_id] = dict(new_system_json_entry)
    data[system_id]['name'] = message.chat.title
    write_systems_json(data)


def update_old_systems_json():
    data = get_systems_json()
    for system in data.keys():
        for prop in new_system_json_entry.keys():
            if prop not in data[system].keys():
                data[system][prop] = new_system_json_entry[prop]
    write_systems_json(data)


def create_chat(message, system_id, typee, link, database):
    chat_tuple = (message.chat.id,
                  system_id,
                  message.chat.title,
                  typee,
                  link,
                  2,  # standart commands
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


# TODO перенести все голосовашки в базу данных или ещё куда-то (JSON)
def create_vote(vote_message):
    """Создаёт голосовашку"""
    log.log_print("create_vote invoked")
    # TODO Параметр purpose, отвечающий за действие, которое надо сделать при закрытии голосовашки
    file = open(votes_file, 'r', encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"time": vote_message.date, "text": vote_message.text,
                                             "favor": {}, "against": {}, "abstain": {}}
    file = open(votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()


def create_multi_vote(vote_message):
    """Создаёт мульти-голосовашку"""
    log.log_print("create_multi_vote invoked")
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    file = open(multi_votes_file, encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"text": vote_message.text, "votes": [], "keyboard": [],
                                             "chat": vote_message.chat.id}
    file = open(multi_votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


def create_adapt_vote(vote_message):
    """Создаёт адапт-голосовашку"""
    log.log_print("create_adapt_vote invoked")
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_adapt_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    file = open(adapt_votes_file, encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"text": vote_message.text, "votes": [], "keyboard": [],
                                             "chat": vote_message.chat.id}
    file = open(adapt_votes_file, 'w', encoding='utf-8')
    file.write(str(votes_shelve))
    file.close()
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


def update_multi_vote(vote_id):
    """Обновляет мульти-голосовашку"""
    log.log_print("update_multi_vote invoked")
    file = open(multi_votes_file, encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
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
    try:
        edit_text(text=text, chat_id=votey['chat'], message_id=vote_id, reply_markup=keyboard, parse_mode="HTML",
                  disable_web_page_preview=True)
    except Exception as e:
        print(e)


def update_adapt_vote(vote_id):
    """Обновляет адапт голосовашку"""
    log.log_print("update_adapt_vote")
    file = open(adapt_votes_file, encoding='utf-8')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
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
    try:
        edit_text(text=text, chat_id=votey['chat'], message_id=vote_id, reply_markup=keyboard, parse_mode="HTML",
                  disable_web_page_preview=True)
    except Exception as e:
        print(e)


def unban_user(person):
    """Remove ban from user"""
    log.log_print("unban_user invoked")
    database = Database()
    # TODO Уточнить систему
    chats_to_unban = database.get_many('chats', ('violators_ban', 2))
    for chat in chats_to_unban:
        if get_member(chat['id'], person.id).status in ('left', 'kicked'):
            unban(chat['id'], person.id)
