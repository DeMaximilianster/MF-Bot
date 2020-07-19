"""Module with functions to send to Telegram servers"""

from telebot.apihelper import ApiException
from presenter.config.token import BOT
import presenter.config.log as log

LOG = log.Logger(log.LOG_TO_CONSOLE)


def handle_errors(function):
    """Ensures fail-safety and logging of possible exceptions"""
    def wrapper(*args, **kwargs):
        try:
            function(*args, **kwargs)
        except ApiException as exception:
            LOG.log(exception)
    return wrapper


@handle_errors
def send(chat_id, message_text, **kwargs):
    """Send a message
    :arg chat_id
    :arg message_text
    :key parse_mode
    :key reply_markup"""
    LOG.log("send invoked")
    return BOT.send_message(chat_id, message_text, disable_web_page_preview=True, **kwargs)


@handle_errors
def send_photo(chat_id, photo, **kwargs):
    """Send a photo
    :arg chat_id
    :arg photo
    :key caption
    :key reply_to_message_id
    :key reply_markup
    :key parse_mode"""
    LOG.log("send_photo invoked")
    return BOT.send_photo(chat_id, photo, **kwargs)


@handle_errors
def send_video(chat_id, video, **kwargs):
    """Send a video
    :arg chat_id
    :arg video
    :key caption
    :key reply_to_message_id
    :key reply_markup
    :key parse_mode"""
    LOG.log("send_video invoked")
    return BOT.send_video(chat_id, video, **kwargs)


@handle_errors
def send_sticker(chat_id, sticker, reply_to_message_id=None):
    """Send a sticker"""
    LOG.log("send_sticker invoked")
    return BOT.send_sticker(chat_id, sticker, reply_to_message_id=reply_to_message_id)


@handle_errors
def send_document(chat_id, data, **kwargs):
    """Send a document
    :arg chat_id
    :arg data
    :key reply_to_message_id
    :key caption
    :key parse_mode"""
    LOG.log("send_document invoked")
    return BOT.send_document(chat_id, data, **kwargs)


@handle_errors
def reply(message, message_text, **kwargs):
    """Reply to a message
    :arg message: message bot replies to
    :arg message_text
    :key parse_mode
    :key reply_markup"""
    LOG.log("reply invoked")
    return BOT.reply_to(message, str(message_text), disable_web_page_preview=True, **kwargs)


@handle_errors
def forward(chat_id, from_chat_id, message_id):
    """Forward a message"""
    LOG.log("forward invoked")
    return BOT.forward_message(chat_id, from_chat_id, message_id)


@handle_errors
def edit_markup(chat_id, message_id, reply_markup=None):
    """Edit buttons of the message"""
    LOG.log("edit_markup invoked")
    return BOT.edit_message_reply_markup(chat_id, message_id, reply_markup=reply_markup)


@handle_errors
def edit_text(text, chat_id, message_id, **kwargs):
    """Edit the text of a message
    :arg text
    :arg chat_id
    :arg message_id
    :key parse_mode
    :key reply_markup"""
    LOG.log("edit_text invoked")
    return BOT.edit_message_text(text, chat_id, message_id,
                                 disable_web_page_preview=True, **kwargs)


@handle_errors
def delete(chat_id, message_id):
    """Delete a message"""
    LOG.log("delete invoked")
    return BOT.delete_message(chat_id, message_id)


@handle_errors
def kick(chat_id, user_id):
    """Kick a user"""
    LOG.log("kick invoked")
    return BOT.kick_chat_member(chat_id, user_id)


@handle_errors
def restrict(chat_id, user_id, **kwargs):
    """Restrict a chat member
    :arg chat_id
    :arg user_id
    :key until_date
    :key can_send_messages
    :key can_send_media_messages
    :key can_send_other_messages
    :key can_add_web_page_previews"""
    LOG.log("restrict invoked")
    return BOT.restrict_chat_member(chat_id, user_id, **kwargs)


@handle_errors
def unban(chat_id, user_id):
    """Unban member"""
    LOG.log("unban invoked")
    return BOT.unban_chat_member(chat_id, user_id)


@handle_errors
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
    LOG.log(f"promote invoked chat_id={chat_id}, user_id={user_id}")
    return BOT.promote_chat_member(chat_id, user_id, **kwargs)


@handle_errors
def answer_inline(inline_query_id, results, cache_time=None):
    """Show a result of an inline-request"""
    LOG.log("answer_inline invoked")
    return BOT.answer_inline_query(inline_query_id, results, cache_time=cache_time)


@handle_errors
def answer_callback(callback_query_id, text=None, show_alert=False):
    """Show a notification on a top of a messsage box (or a alert)"""
    LOG.log("answer_callback invoked")
    return BOT.answer_callback_query(callback_query_id, text, show_alert)


@handle_errors
def register_handler(sent, function, *args, **kwargs):
    """Next message will be processed with specified function"""
    LOG.log("register_handler invoked")
    return BOT.register_next_step_handler(sent, function, *args, **kwargs)


@handle_errors
def get_member(chat_id, user_id):
    """Get a member of a chat"""
    LOG.log("get_member invoked")
    return BOT.get_chat_member(chat_id, user_id)


@handle_errors
def get_chat(chat_id):
    """Get a chat"""
    LOG.log("get_chat invoked")
    return BOT.get_chat(chat_id)


@handle_errors
def get_me():
    """ Get information about bot """
    LOG.log("get_me invoked")
    return BOT.get_me()