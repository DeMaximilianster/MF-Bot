from presenter.config.token import BOT
import presenter.config.log as log

log = log.Loger(log.LOG_TO_CONSOLE)


def send(chat_id, message_text, parse_mode=None, reply_markup=None, disable_web_page_preview=True):
    """Отправить сообщение"""
    log.log_print("send invoked")
    try:
        return BOT.send_message(chat_id,
                                message_text,
                                parse_mode=parse_mode,
                                reply_markup=reply_markup,
                                disable_web_page_preview=disable_web_page_preview)
    except Exception as e:
        log.log_print(e)


def send_photo(chat_id,
               photo,
               caption=None,
               reply_to_message_id=None,
               reply_markup=None,
               parse_mode=None):
    """Отправить фото"""
    log.log_print("send_photo invoked")
    try:
        return BOT.send_photo(chat_id,
                              photo,
                              caption=caption,
                              reply_to_message_id=reply_to_message_id,
                              reply_markup=reply_markup,
                              parse_mode=parse_mode)
    except Exception as e:
        log.log_print(e)


def send_video(chat_id,
               video,
               caption=None,
               reply_to_message_id=None,
               reply_markup=None,
               parse_mode=None):
    """Отправить видео"""
    log.log_print("send_video invoked")
    try:
        return BOT.send_video(chat_id,
                              video,
                              caption=caption,
                              reply_to_message_id=reply_to_message_id,
                              reply_markup=reply_markup,
                              parse_mode=parse_mode)
    except Exception as e:
        log.log_print(e)


def send_sticker(chat_id, sticker, reply_to_message_id=None):
    """Отправить стикер"""
    log.log_print("send_sticker invoked")
    try:
        return BOT.send_sticker(chat_id, sticker, reply_to_message_id=reply_to_message_id)
    except Exception as e:
        log.log_print(e)


def send_document(chat_id, data, reply_to_message_id=None, caption=None, parse_mode=None):
    log.log_print("send_document invoked")
    try:
        return BOT.send_document(chat_id, data, reply_to_message_id, caption, parse_mode=parse_mode)
    except Exception as e:
        log.log_print(e)


def reply(message, message_text, parse_mode=None, reply_markup=None,
          disable_web_page_preview=True):
    """Ответить на сообщение"""
    log.log_print("reply invoked")
    try:
        return BOT.reply_to(message,
                            message_text,
                            parse_mode=parse_mode,
                            reply_markup=reply_markup,
                            disable_web_page_preview=disable_web_page_preview)
    except Exception as e:
        log.log_print(e)


def forward(chat_id, from_chat_id, message_id):
    """Переслать сообщение"""
    log.log_print("forward invoked")
    try:
        return BOT.forward_message(chat_id, from_chat_id, message_id)
    except Exception as e:
        log.log_print(e)


def edit_markup(chat_id, message_id, reply_markup=None):
    """Отредактировать кнопки сообщения"""
    log.log_print("edit_markup invoked")
    try:
        return BOT.edit_message_reply_markup(chat_id, message_id, reply_markup=reply_markup)
    except Exception as e:
        log.log_print(e)


def edit_text(text,
              chat_id,
              message_id,
              parse_mode=None,
              reply_markup=None,
              disable_web_page_preview=True):
    """Отредактировать текст сообщения"""
    log.log_print("edit_text invoked")
    try:
        return BOT.edit_message_text(text,
                                     chat_id,
                                     message_id,
                                     parse_mode=parse_mode,
                                     reply_markup=reply_markup,
                                     disable_web_page_preview=disable_web_page_preview)
    except Exception as e:
        log.log_print(e)


def delete(chat_id, message_id):
    """Удаляет сообщение"""
    log.log_print("delete invoked")
    try:
        return BOT.delete_message(chat_id, message_id)
    except Exception as e:
        log.log_print(e)


def kick(chat_id, user_id, until_date=60):
    """Кикнуть участника"""
    log.log_print("kick invoked")
    try:
        return BOT.kick_chat_member(chat_id, user_id, until_date)
    except Exception as e:
        log.log_print(e)


def restrict(chat_id,
             user_id,
             until_date=None,
             can_send_messages=None,
             can_send_media_messages=None,
             can_send_other_messages=None,
             can_add_web_page_previews=None):
    """Restrict chat member"""
    log.log_print("restrict invoked")
    try:
        return BOT.restrict_chat_member(chat_id=chat_id,
                                        user_id=user_id,
                                        until_date=until_date,
                                        can_send_messages=can_send_messages,
                                        can_send_media_messages=can_send_media_messages,
                                        can_send_other_messages=can_send_other_messages,
                                        can_add_web_page_previews=can_add_web_page_previews)
    except Exception as e:
        log.log_print(e)


def unban(chat_id, user_id):
    """Unban member"""
    log.log_print(f"unban invoked")
    try:
        return BOT.unban_chat_member(chat_id, user_id)
    except Exception as e:
        log.log_print(e)


def promote(chat_id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False):
    """Изменить админские полномочия"""
    log.log_print(f"promote invoked chat_id={chat_id}, user_id={user_id}")
    try:
        return BOT.promote_chat_member(chat_id,
                                       user_id,
                                       can_change_info=can_change_info,
                                       can_post_messages=can_post_messages,
                                       can_edit_messages=can_edit_messages,
                                       can_delete_messages=can_delete_messages,
                                       can_invite_users=can_invite_users,
                                       can_restrict_members=can_restrict_members,
                                       can_pin_messages=can_pin_messages,
                                       can_promote_members=can_promote_members)
    except Exception as e:
        log.log_print(e)


def answer_inline(inline_query_id, results, cache_time=None):
    """Выдаёт инлайн-результат"""
    log.log_print("answer_inline invoked")
    try:
        return BOT.answer_inline_query(inline_query_id, results, cache_time=cache_time)
    except Exception as e:
        log.log_print(e)


def answer_callback(callback_query_id, text=None, show_alert=False):
    """Выдаёт инлайн-результат"""
    log.log_print("answer_callback invoked")
    try:
        return BOT.answer_callback_query(callback_query_id, text, show_alert)
    except Exception as e:
        log.log_print(e)


def register_handler(sent, function, *args, **kwargs):
    """Следующее сообщение будет обработано заданной функцией"""
    log.log_print("register_handler invoked")
    try:
        return BOT.register_next_step_handler(sent, function, *args, **kwargs)
    except Exception as e:
        log.log_print(e)


def get_member(chat_id, user_id):
    """Получить участника чата"""
    log.log_print("get_member invoked")
    try:
        return BOT.get_chat_member(chat_id, user_id)
    except Exception as e:
        log.log_print(e)


def get_chat(chat_id):
    """Получить чат"""
    log.log_print("get_chat invoked")
    try:
        return BOT.get_chat(chat_id)
    except Exception as e:
        log.log_print(e)


def get_me():
    """ Get information about bot """
    log.log_print("get_me invoked")
    try:
        return BOT.get_me()
    except Exception as e:
        log.log_print(e)
