"""Commands for developers to test some stuff"""

from time import ctime, time

from presenter.config.config_func import time_replace, entities_saver, get_text_and_entities, \
    get_target_message, value_marker
from presenter.config.config_func import code_text_wrapper as cd
from presenter.config.log import Logger
from view.output import reply, get_me, get_member

LOG = Logger()


def show_id(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    LOG.log_print(str(message.from_user.id) + ": show_id invoked")

    answer = f'Время отправки вашего сообщения: {cd(ctime(message.date))}\n\n' \
             f'Переводя, выходит: {cd(time_replace(message.date))}\n\n' \
             f'Время отправки моего сообщения: {cd(ctime(time()))}\n\n' \
             f'ID этого чата: {cd(message.chat.id)}\n\n' \
             f'Ваш ID: {cd(message.from_user.id)}\n\n' \
             f'Ваш language code: {cd(message.from_user.language_code)}\n\n' \
             f'ID вашего сообщения: {cd(message.message_id)}\n\n'

    reply_msg = message.reply_to_message
    if reply_msg is not None:  # Сообщение является ответом

        answer += f'ID человека, на сообщение которого ответили: {cd(reply_msg.from_user.id)}\n\n' \
                  f'Его/её language code: {cd(reply_msg.from_user.language_code)}\n\n' \
                  f'ID сообщения, на которое ответили: {cd(reply_msg.message_id)}\n\n' \
                  f'Время отправки сообщения, на которое вы ответили: ' \
                  f'{cd(ctime(reply_msg.date))}\n\n' \
                  f'Переводя, выходит: {cd(time_replace(reply_msg.date))}\n\n'
        if reply_msg.forward_from is not None:  # Сообщение, на которое ответили, является форвардом
            answer += f'ID человека, написавшего пересланное сообщение: ' \
                      f'{cd(reply_msg.forward_from.id)}\n\n' \
                      f'Его/её language code: {cd(reply_msg.forward_from.language_code)}\n\n'
        # Replied message is forwarded from a channel
        elif reply_msg.forward_from_chat:
            answer += f'ID канала, из которого переслали сообщение: ' \
                      f'{cd(reply_msg.forward_from_chat.id)}\n\n'

        if reply_msg.sticker is not None:
            answer += f'ID стикера: {cd(reply_msg.sticker.file_id)}\n'
            if reply_msg.sticker.set_name:
                answer += 'Ссылка на набор с этим стикером: https://telegram.me/addstickers/'
                answer += reply_msg.sticker.set_name + '\n\n'
            else:
                answer += 'У этого стикера нет своего набора\n\n'

        elif reply_msg.photo is not None:
            answer += f'ID фотографии: {cd(reply_msg.photo[0].file_id)}'
            for i in reply_msg.photo[1:]:
                answer += f',\n{cd(i.file_id)}'
            answer += '\n\n'

        for media in (reply_msg.video, reply_msg.voice, reply_msg.video_note, reply_msg.audio,
                      reply_msg.document):
            if media:
                answer += f'ID медиа: {cd(media.file_id)}\n\n'
                break
    reply(message, answer, parse_mode='HTML')


def echo_message(message):
    """Echo message with saving all highlights"""
    target_message = get_target_message(message)
    text, entities = get_text_and_entities(target_message)
    if text:
        reply(message, entities_saver(text, entities), parse_mode='HTML')
    else:
        reply(message, "У этого сообщения нет текста")


def clear_echo_message(message):
    """Echo message but unparse all highlights (bold text -> <b>text</b>)"""
    target_message = get_target_message(message)
    text, entities = get_text_and_entities(target_message)
    if text:
        reply(message, entities_saver(text, entities))
    else:
        reply(message, "У этого сообщения нет текста")


def html_echo_message(message):
    """Echo message but parse all entities in the text (like <b>bold</b>)"""
    target_message = get_target_message(message)
    text = target_message.text
    if text:
        rep = reply(message, text, parse_mode='HTML')
        if rep is None:
            reply(message, "Не могу распарсить это сообщение")
    else:
        reply(message, "У этого сообщения нет текста")


def get_bot_rights(message):
    """Check bot admin rights in the current chat"""
    info = get_member(message.chat.id, get_me().id)
    response = f'''Полномочия бота:

{value_marker(info.can_change_info, '✅', '❌')} Изменение профиля группы  
{value_marker(info.can_delete_messages, '✅', '❌')} Удаление сообщений  
{value_marker(info.can_restrict_members, '✅', '❌')} Блокировка участников  
{value_marker(info.can_invite_users, '✅', '❌')} Пригласительные ссылки  
{value_marker(info.can_pin_messages, '✅', '❌')} Закрепление сообщений  
{value_marker(info.can_promote_members, '✅', '❌')} Добавление администраторов
'''
    reply(message, response)


def simulate_error(message):
    """Simulates an error"""
    reply(message, "Запускаю ошибку!")
    reply(message, 5/0)
