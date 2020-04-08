"""Module with functions to send to Telegram servers"""

from presenter.config.token import BOT
import presenter.config.log as log

LOG = log.Loger(log.LOG_TO_CONSOLE)


def send(chat_id, message_text, **kwargs):
    """Send a message
    :arg chat_id
    :arg message_text
    :key parse_mode
    :key reply_markup
    :key disable_web_page_preview"""
    LOG.log_print("send invoked")
    return BOT.send_message(chat_id, message_text, **kwargs)


def send_photo(chat_id, photo, **kwargs):
    """Send a photo
    :arg chat_id
    :arg photo
    :key caption
    :key reply_to_message_id
    :key reply_markup
    :key parse_mode"""
    LOG.log_print("send_photo invoked")
    return BOT.send_photo(chat_id, photo, **kwargs)


def send_video(chat_id, video, **kwargs):
    """Send a video
    :arg chat_id
    :arg video
    :key caption
    :key reply_to_message_id
    :key reply_markup
    :key parse_mode"""
    LOG.log_print("send_video invoked")
    return BOT.send_video(chat_id, video, **kwargs)


def send_sticker(chat_id, sticker, reply_to_message_id=None):
    """Send a sticker"""
    LOG.log_print("send_sticker invoked")
    return BOT.send_sticker(chat_id, sticker, reply_to_message_id=reply_to_message_id)


def send_document(chat_id, data, **kwargs):
    """Send a document
    :arg chat_id
    :arg data
    :key reply_to_message_id
    :key caption
    :key parse_mode"""
    LOG.log_print("send_document invoked")
    return BOT.send_document(chat_id, data, **kwargs)


def reply(message, message_text, **kwargs):
    """Reply to a message
    :arg message: message bot replies to
    :arg message_text
    :key parse_mode
    :key reply_markup
    :key disable_web_page_preview"""
    LOG.log_print("reply invoked")
    return BOT.reply_to(message, message_text, **kwargs)


def forward(chat_id, from_chat_id, message_id):
    """Forward a message"""
    LOG.log_print("forward invoked")
    return BOT.forward_message(chat_id, from_chat_id, message_id)


def edit_markup(chat_id, message_id, reply_markup=None):
    """Edit buttons of the message"""
    LOG.log_print("edit_markup invoked")
    return BOT.edit_message_reply_markup(chat_id, message_id, reply_markup=reply_markup)


def edit_text(text, chat_id, message_id, **kwargs):
    """Edit the text of a message
    :arg text
    :arg chat_id
    :arg message_id
    :key parse_mode
    :key reply_markup
    :key disable_web_page_preview"""
    LOG.log_print("edit_text invoked")
    return BOT.edit_message_text(text, chat_id, message_id, **kwargs)


def delete(chat_id, message_id):
    """Delete a message"""
    LOG.log_print("delete invoked")
    return BOT.delete_message(chat_id, message_id)


def kick(chat_id, user_id):
    """Kick a user"""
    LOG.log_print("kick invoked")
    return BOT.kick_chat_member(chat_id, user_id)


def restrict(chat_id, user_id, **kwargs):
    """Restrict a chat member
    :arg chat_id
    :arg user_id
    :key until_date
    :key can_send_messages
    :key can_send_media_messages
    :key can_send_other_messages
    :key can_add_web_page_previews"""
    LOG.log_print("restrict invoked")
    return BOT.restrict_chat_member(chat_id, user_id, **kwargs)


def unban(chat_id, user_id):
    """Unban member"""
    LOG.log_print("unban invoked")
    return BOT.unban_chat_member(chat_id, user_id)


def promote(chat_id, user_id, **kwargs):
    """Change admin permissions of a person
    :arg chat_id
    :arg user_id
    :key can_change_info
    :key can_post_messages
    :key can_edit_messages
    :key can_delete_messages
    :key can_invite_users
    :key can_restrict_members
    :key can_pin_messages
    :key can_promote_members"""
    LOG.log_print(f"promote invoked chat_id={chat_id}, user_id={user_id}")
    return BOT.promote_chat_member(chat_id, user_id, **kwargs)


def answer_inline(inline_query_id, results, cache_time=None):
    """Show a result of an inline-request"""
    LOG.log_print("answer_inline invoked")
    return BOT.answer_inline_query(inline_query_id, results, cache_time=cache_time)


def answer_callback(callback_query_id, text=None, show_alert=False):
    """Show a notification on a top of a messsage box (or a alert)"""
    LOG.log_print("answer_callback invoked")
    return BOT.answer_callback_query(callback_query_id, text, show_alert)


def register_handler(sent, function, *args, **kwargs):
    """Next message will be processed with specified function"""
    LOG.log_print("register_handler invoked")
    return BOT.register_next_step_handler(sent, function, *args, **kwargs)


def get_member(chat_id, user_id):
    """Get a member of a chat"""
    LOG.log_print("get_member invoked")
    return BOT.get_chat_member(chat_id, user_id)


def get_chat(chat_id):
    """Get a chat"""
    LOG.log_print("get_chat invoked")
    return BOT.get_chat(chat_id)


def get_me():
    """ Get information about bot """
    LOG.log_print("get_me invoked")
    return BOT.get_me()
