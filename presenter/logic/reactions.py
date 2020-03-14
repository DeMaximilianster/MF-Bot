# -*- coding: utf-8 -*-
"""Module with reactions bot does if there's no certain command"""
from time import time
from presenter.config.log import Loger, log_to
from presenter.config.config_func import Database, is_suitable, \
    feature_is_available, get_system_configs, create_captcha_keyboard, \
    create_chat, CaptchaBan, person_info_in_html, chat_info_in_html, html_cleaner
from view.output import delete, kick, send, promote, reply, restrict

LOG = Loger(log_to)


def trigger(message):
    """Reacts to some triggers in people's messages"""
    database = Database()
    chat_id = message.chat.id
    chat = database.get('chats', ('id', chat_id))
    system_id = chat['system']
    content_type = 'text'
    if message.voice:
        content_type = 'voice'
    trigger_entry = database.get('triggers', ('id', chat_id), ('sys_or_chat', 'chat'),
                                 ('content_type', content_type))
    if not trigger_entry:
        trigger_entry = database.get('triggers', ('id', system_id), ('sys_or_chat', 'system'),
                                     ('content_type', content_type))
    if trigger_entry:
        if trigger_entry['to_delete']:
            delete(chat_id, message.message_id)
        user = message.from_user
        print(user)
        text = str(trigger_entry['text_ans']).format(username=user.username,
                                                     nickname=user.first_name,
                                                     user_id=user.id)
        send(chat_id, text, parse_mode='HTML')


def new_member(message, member):
    """Реагирует на вход в чат"""
    LOG.log_print(f"new_member invoked")
    database = Database()
    # Declaring variables
    text = ''
    keyboard = None
    captcha = False
    sent = None
    name = html_cleaner(member.first_name)
    system = database.get('chats', ('id', message.chat.id))['system']
    chat_configs = get_system_configs(system)
    if database.get('members', ('id', member.id), ('rank', chat_configs['ranks'][0])) and \
            feature_is_available(message.chat.id, system, 'violators_ban'):
        kick(message.chat.id, member.id)
    elif is_suitable(message, member, 'uber', loud=False) and feature_is_available(
            message.chat.id, system, 'admins_promote'):
        promote(message.chat.id,
                member.id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True)
        text += chat_configs['greetings']['full_admin'].format(name=name)
    elif is_suitable(message, member, 'boss', loud=False) and feature_is_available(
            message.chat.id, system, 'admins_promote'):
        promote(message.chat.id,
                member.id,
                can_change_info=False,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=False)
        text += chat_configs['greetings']['admin'].format(name=name)
    elif feature_is_available(message.chat.id, system, 'newbies_captched') and \
            member.id == message.from_user.id and time() - message.date < 60:
        text = chat_configs['greetings']['captcha'].format(name=name)
        keyboard = create_captcha_keyboard()
        captcha = True
    else:
        text = chat_configs['greetings']['standart'].format(name=name)
    # TODO Немнжко по быдлокодерски устроено неудаление сообщения о входе
    if feature_is_available(message.chat.id, system, 'moves_delete') and not feature_is_available(
            message.chat.id, system, 'newbies_captched'):
        delete(message.chat.id, message.message_id)
    else:
        sent = reply(message,
                     text,
                     reply_markup=keyboard,
                     parse_mode='HTML',
                     disable_web_page_preview=True)
    # Notify admins if admin's chat exists
    admin_place = database.get('systems', ('id', system))['admin_place']
    if admin_place:
        text = f'{person_info_in_html(member)} теперь в {chat_info_in_html(message.chat)}'
        send(admin_place, text, parse_mode="HTML")
    if captcha:
        restrict(message.chat.id, member.id, until_date=time() + 300)
        captcha_ban = CaptchaBan(message, sent)
        captcha_ban.start()


def left_member(message):
    """Комментирует уход участника и прощается участником"""
    LOG.log_print("left_member invoked")
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
    elif feature_is_available(message.chat.id, system, 'moves_delete'):  # Чела забанили
        delete(message.chat.id, message.message_id)
    # Notify admins if admin's chat exists
    admin_place = database.get('systems', ('id', system))['admin_place']
    if admin_place:
        text = f'{person_info_in_html(member)} теперь не в {chat_info_in_html(message.chat)}'
        send(admin_place, text, parse_mode='HTML')


def chat_id_update(message):
    """Update chat id if group converts to supergroup"""
    LOG.log_print("chat_id_update invoked")
    database = Database()
    old_chat = database.get('chats', ('id', message.migrate_from_chat_id))
    if old_chat:
        chat_type = 'private'
        link = 'None'
        if message.chat.username:
            chat_type = 'public'
            link = message.chat.username
        create_chat(message, old_chat['system'], chat_type, link, database)
