# -*- coding: utf-8 -*-
from presenter.config.config_func import Database, time_replace, is_suitable, feature_is_available, get_system_configs,\
    create_chat, CaptchaBan
from view.output import delete, kick, send, promote, reply, restrict
from presenter.config.log import Loger, log_to
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from time import time
from random import shuffle

log = Loger(log_to)


def trigger(message):
    database = Database()
    chat_id = message.chat.id
    chat = database.get('chats', ('id', chat_id))
    system_id = chat['system']
    content_type = 'text'
    if message.voice:
        content_type = 'voice'
    trigger_entry = database.get('triggers', ('id', chat_id), ('sys_or_chat', 'chat'), ('content_type', content_type))
    if not trigger_entry:
        trigger_entry = database.get('triggers', ('id', system_id), ('sys_or_chat', 'system'),
                                     ('content_type', content_type))
    if trigger_entry:
        if trigger_entry['to_delete']:
            delete(chat_id, message.message_id)
        user = message.from_user
        print(user)
        text = str(trigger_entry['text_ans']).format(username=user.username, nickname=user.first_name, user_id=user.id)
        send(chat_id, text, parse_mode='HTML')


def deleter(message):
    """Удаляет медиа ночью"""
    log.log_print("deleter invoked")
    database = Database()
    # Получаем из БД переменную, отвечающую за работу это функции
    delete_mode = database.get('config', ('var', 'delete'))['value']

    if not delete_mode:
        return None
    if time_replace(message.date)[1] >= 22 or time_replace(message.date)[1] < 8:  # Время, когда надо удалять
        database = Database()
        rank = database.get('members', ('id', message.from_user.id))['rank']
        if rank == 'Guest':
            # TODO бот делает это предупреждение не чаще раза в 24 часа на человека
            ans = "Э, нет, в такое время медиа нельзя присылать гостям чата. "
            ans += "Если вы не гость, то обратитесь к Дэ'Максу"
            send(message.chat.id, ans)
            delete(message.chat.id, message.message_id)


def new_member(message, member):
    """Реагирует на вход в чат"""
    log.log_print(f"new_member invoked")
    database = Database()
    # Declaring variables
    answer = ''
    keyboard = None
    captcha = False
    sent = None

    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    chat_configs = get_system_configs(system)
    if database.get('members', ('id', member.id), ('rank', chat_configs['ranks'][0])) and feature_is_available(
            message.chat.id, system, 'violators_ban'):
        kick(message.chat.id, member.id)
    elif is_suitable(message, member, 'uber', loud=False) and feature_is_available(
            message.chat.id, system, 'admins_promote'):
        promote(message.chat.id, member.id,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=True)
        answer += chat_configs['greetings']['full_admin'].format(name=member.first_name)
    elif is_suitable(message, member, 'boss', loud=False) and feature_is_available(
            message.chat.id, system, 'admins_promote'):
        promote(message.chat.id, member.id,
                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
        answer += chat_configs['greetings']['admin'].format(name=member.first_name)
    elif feature_is_available(message.chat.id, system, 'newbies_captched'):
        answer = chat_configs['greetings']['captcha'].format(name=member.first_name)
        wrong_animals_string = '🦀🦞🦑🐡🐶🐱🐭🐹🐰🦊🐻🐼🐵🐸🐷🐮🦁🐯🐨🙈🙉🙊🐒🐔🐧🐦🐤🐗🐺🦇🦉🦅🦆🐥🐣🐴🦄'
        wrong_animals_string += '🐝🐛🦋🐌🐞🐜🦎🐍🐢🦂🕷🦗🦟🐆🦓🦍🐘🦛🦏🐪🐫🐏🐖🐎🦔🐈'
        wrong_animals_buttons = []
        for wrong_animal in wrong_animals_string:
            wrong_animals_buttons.append(InlineKeyboardButton(wrong_animal, callback_data="captcha_fail"))
        buttons = [InlineKeyboardButton("🦐", callback_data="captcha")] + wrong_animals_buttons
        shuffle(buttons)
        buttons_rows = list([buttons[i:i+8] for i in range(0, len(buttons), 8)])
        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 8
        for buttons_row in buttons_rows:
            keyboard.add(*buttons_row)
        captcha = True
    else:
        answer = chat_configs['greetings']['standart'].format(name=member.first_name)
    # TODO Немнжко по быдлокодерски устроено неудаление сообщения о входе
    if feature_is_available(message.chat.id, system, 'moves_delete') and not feature_is_available(
            message.chat.id, system, 'newbies_captched'):
        delete(message.chat.id, message.message_id)
    else:
        sent = reply(message, answer, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)
    # Notify admins if admin's chat exists
    admin_place = database.get('systems', ('id', system))['admin_place']
    if admin_place:
        send(admin_place, f'<a href="tg://user?id={member.id}">{html_cleaner(member.first_name)}</a>'\
        f' (@{html_cleaner(member.username)}) [{member.id}] теперь в {html_cleaner(message.chat.title)}',
        parse_mode="HTML")
    if captcha:
        restrict(chat['id'], member.id, until_date=time() + 300)
        captcha_ban = CaptchaBan(message, sent)
        captcha_ban.start()


def left_member(message):
    """Комментирует уход участника и прощается участником"""
    log.log_print("left_member invoked")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    if chat['type'] == 'private':
        chat = chat['name']
    else:
        chat = '@' + chat['link']
    member = message.left_chat_member
    if message.from_user.id == member.id:  # Чел вышел самостоятельно
        if feature_is_available(message.chat.id, system, 'moves_delete'):
            delete(message.chat.id, message.message_id)
        else:
            reply(message, "Минус чувачок")
        send(member.id, 'До встречи в ' + chat)
    else:  # Чела забанили
        delete(message.chat.id, message.message_id)
    # Notify admins if admin's chat exists
    admin_place = database.get('systems', ('id', system))['admin_place']
    if admin_place:
        send(admin_place, '{} (@{}) [{}] теперь не в {}'.format(member.first_name, member.username, member.id,
                                                                message.chat.title))


def chat_id_update(message):
    log.log_print("chat_id_update invoked")
    database = Database()
    old_chat = database.get('chats', ('id', message.migrate_from_chat_id))
    if old_chat:
        typee = 'private'
        link = 'None'
        if message.chat.username:
            typee = 'public'
            link = message.chat.username
        create_chat(message, old_chat['system'], typee, link, database)
