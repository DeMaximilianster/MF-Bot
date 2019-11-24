from presenter.config.token import bot
import presenter.config.log as log

log = log.Loger(log.LOG_TO_CONSOLE)


def send(chat_id, message_text, parse_mode=None, reply_markup=None, disable_web_page_preview=False):
    """Отправить сообщение"""
    log.log_print("send invoked")
    try:
        return bot.send_message(chat_id, message_text, parse_mode=parse_mode, reply_markup=reply_markup,
                                disable_web_page_preview=disable_web_page_preview)
    except Exception as e:
        log.log_print(e)


def send_photo(chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None, parse_mode=None):
    """Отправить фото"""
    log.log_print("send_photo invoked")
    try:
        return bot.send_photo(chat_id, photo, caption=caption, reply_to_message_id=reply_to_message_id,
                              reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        log.log_print(e)


def send_video(chat_id, video, caption=None, reply_to_message_id=None, reply_markup=None, parse_mode=None):
    """Отправить видео"""
    log.log_print("send_video invoked")
    try:
        return bot.send_video(chat_id, video, caption=caption, reply_to_message_id=reply_to_message_id,
                              reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        log.log_print(e)


def send_sticker(chat_id, sticker, reply_to_message_id=None):
    """Отправить стикер"""
    log.log_print("send_sticker invoked")
    try:
        return bot.send_sticker(chat_id, sticker, reply_to_message_id=reply_to_message_id)
    except Exception as e:
        log.log_print(e)


def reply(message, message_text, parse_mode=None, reply_markup=None, disable_web_page_preview=False):
    """Ответить на сообщение"""
    log.log_print("reply invoked")
    try:
        return bot.reply_to(message, message_text, parse_mode=parse_mode, reply_markup=reply_markup,
                            disable_web_page_preview=disable_web_page_preview)
    except Exception as e:
        log.log_print(e)


def forward(chat_id, from_chat_id, message_id):
    """Переслать сообщение"""
    log.log_print("forward invoked")
    try:
        return bot.forward_message(chat_id, from_chat_id, message_id)
    except Exception as e:
        log.log_print(e)


def edit_markup(chat_id, message_id, reply_markup=None):
    """Отредактировать кнопки сообщения"""
    log.log_print("edit_markup invoked")
    try:
        return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=reply_markup)
    except Exception as e:
        log.log_print(e)


def edit_text(text, chat_id, message_id, parse_mode=None, reply_markup=None):
    """Отредактировать текст сообщения"""
    log.log_print("edit_text invoked")
    try:
        return bot.edit_message_text(text, chat_id, message_id, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        log.log_print(e)


def delete(chat_id, message_id):
    """Удаляет сообщение"""
    log.log_print("delete invoked")
    try:
        return bot.delete_message(chat_id, message_id)
    except Exception as e:
        log.log_print(e)


def kick(chat_id, user_id, until_date=None):
    """Кикнуть участника"""
    log.log_print("kick invoked")
    try:
        return bot.kick_chat_member(chat_id, user_id, until_date)
    except Exception as e:
        log.log_print(e)


def promote(chat_id, user_id, can_change_info=False, can_post_messages=False, can_edit_messages=False,
            can_delete_messages=False, can_invite_users=False, can_restrict_members=False, can_pin_messages=False,
            can_promote_members=False):
    """Изменить админские полномочия"""
    log.log_print("promote invoked")
    try:
        return bot.promote_chat_member(chat_id, user_id,
                                       can_change_info=can_change_info, can_post_messages=can_post_messages,
                                       can_edit_messages=can_edit_messages, can_delete_messages=can_delete_messages,
                                       can_invite_users=can_invite_users, can_restrict_members=can_restrict_members,
                                       can_pin_messages=can_pin_messages, can_promote_members=can_promote_members)
    except Exception as e:
        log.log_print(e)


def answer_inline(inline_query_id, results, cache_time=None):
    """Выдаёт инлайн-результат"""
    log.log_print("answer_inline invoked")
    try:
        return bot.answer_inline_query(inline_query_id, results, cache_time=cache_time)
    except Exception as e:
        log.log_print(e)


def answer_callback(callback_query_id, text=None):
    """Выдаёт инлайн-результат"""
    log.log_print("answer_callback invoked")
    try:
        return bot.answer_callback_query(callback_query_id, text)
    except Exception as e:
        log.log_print(e)


def register_handler(sent, function, *args, **kwargs):
    """Следующее сообщение будет обработано заданной функцией"""
    log.log_print("register_handler invoked")
    try:
        return bot.register_next_step_handler(sent, function, *args, **kwargs)
    except Exception as e:
        log.log_print(e)


def get_member(chat_id, user_id):
    """Получить участника чата"""
    log.log_print("get_member invoked")
    try:
        return bot.get_chat_member(chat_id, user_id)
    except Exception as e:
        log.log_print(e)


def get_chat(chat_id):
    """Получить чат"""
    log.log_print("get_chat invoked")
    try:
        return bot.get_chat(chat_id)
    except Exception as e:
        log.log_print(e)
