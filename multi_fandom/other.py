from multi_fandom.config.config_var import *
other_work = True


@bot.message_handler(content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice',
                                    'location', 'contact', 'new_chat_members', 'left_chat_member', 'new_chat_title',
                                    'new_chat_photo', 'delete_chat_photo'])
def texter(message):
    """Подсчитывает сообщения"""
    if message.chat.id != -1001408293838:  # Только сообщения в главном чате
        return None
    counter(message)
