from time import ctime, time

from presenter.config.config_func import time_replace, entities_saver, get_text_and_entities, get_target_message
from presenter.config.config_func import code_text_wrapper as cd
from presenter.config.log import Loger
from view.output import reply

log = Loger()


def show_id(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    log.log_print(str(message.from_user.id) + ": show_id invoked")

    answer = f'Время отправки вашего сообщения: {cd(ctime(message.date))}\n\n'\
             f'Переводя, выходит: {cd(time_replace(message.date))}\n\n'\
             f'Время отправки моего сообщения: {cd(ctime(time()))}\n\n'\
             f'ID этого чата: {cd(message.chat.id)}\n\n'\
             f'Ваш ID: {cd(message.from_user.id)}\n\n'\
             f'Ваш language code: {cd(message.from_user.language_code)}\n\n'\
             f'ID вашего сообщения: {cd(message.message_id)}\n\n'

    reply_msg = message.reply_to_message
    if reply_msg is not None:  # Сообщение является ответом

        answer += f'ID человека, на сообщение которого ответили: {cd(reply_msg.from_user.id)}\n\n'\
                  f'Его/её language code: {cd(reply_msg.from_user.language_code)}\n\n'\
                  f'ID сообщения, на которое ответили: {cd(reply_msg.message_id)}\n\n'\
                  f'Время отправки сообщения, на которое вы ответили: {cd(ctime(reply_msg.date))}\n\n' \
                  f'Переводя, выходит: {cd(time_replace(reply_msg.date))}\n\n'
        if reply_msg.forward_from is not None:  # Сообщение, на которое ответили, является форвардом
            answer += f'ID человека, написавшего пересланное сообщение: {cd(reply_msg.forward_from.id)}\n\n'\
                      f'Его/её language code: {cd(reply_msg.forward_from.language_code)}\n\n'

        elif reply_msg.forward_from_chat:  # Сообщение, на которое ответили, является форвардом из канала
            answer += f'ID канала, из которого переслали сообщение: {cd(reply_msg.forward_from_chat.id)}\n\n'

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

        for media in (reply_msg.video, reply_msg.voice, reply_msg.video_note, reply_msg.audio, reply_msg.document):
            if media:
                answer += f'ID медиа: {cd(media.file_id)}\n\n'
                break
    reply(message, answer, parse_mode='HTML')


def echo_message(message):
    target_message = get_target_message(message)
    text, entities = get_text_and_entities(target_message)
    if text:
        reply(message, entities_saver(text, entities), parse_mode='HTML')
    else:
        reply(message, "У этого сообщения нет текста")


def clear_echo_message(message):
    target_message = get_target_message(message)
    text, entities = get_text_and_entities(target_message)
    if text:
        reply(message, entities_saver(text, entities))
    else:
        reply(message, "У этого сообщения нет текста")


def html_echo_message(message):
    target_message = get_target_message(message)
    text = target_message.text
    if text:
        rep = reply(message, text, parse_mode='HTML')
        if not rep:
            reply(message, "Не могу распарсить это сообщение")
    else:
        reply(message, "У этого сообщения нет текста")
