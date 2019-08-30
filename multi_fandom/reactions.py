# -*- coding: utf-8 -*-
from multi_fandom.config.config_var import *
reactions_work = True


@bot.message_handler(content_types=['document', 'photo', 'sticker', 'video', 'video_note'])
def deleter(message):
    """Удаляет медиа ночью"""
    if not in_mf(message):  # Если это не МФ2, то какая разница?
        return None
    database = Database()
    delete = database.get('delete', 'config', 'var')[1]  # Получаем из БД переменную, отвечающую за работу это функции
    del database
    if not delete:
        return None
    if time_replace(message.date)[1] >= 22 or time_replace(message.date)[1] < 8:  # Время, когда надо удалять
        database = Database()
        rank = database.get(message.from_user.id)[3]
        if rank == 'Гость' or rank == 'Кто-то':
            # TODO бот делает это предупреждение не чаще раза в 24 часа на человека

            #  ans = "Э, нет, в такое время медиа нельзя присылать гостям чата. "
            #  ans += "Если вы не гость, то обратитесь к Дэ'Максу"
            #  bot.send_message(message.chat.id, ans)
            bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    """Реагирует на вход в чат"""
    if not in_mf(message):
        return None
    database = Database()
    member = message.new_chat_members[0]
    answer = ''
    rank = database.get(member.id)[3]  # Получаем его звание
    if member.is_bot:
        bot.send_message(message.chat.id, "Ещё один бот, вряд-ли более умный, чем я")
    if rank == "Нарушитель":
        bot.kick_chat_member(message.chat.id, member.id)
    elif rank == "Админ" or rank == "Член Комитета":
        bot.promote_chat_member(message.chat.id, member.id,
                                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
        answer += "О, добро пожаловать, держи админку"
    elif rank == "Заместитель":
        bot.promote_chat_member(message.chat.id, member.id,
                                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                                can_restrict_members=True, can_pin_messages=True, can_promote_members=True)
        answer += "О, добро пожаловать, держи полную админку"
    else:  # У нового участника нет особенностей
        answer = 'Добро пожаловать, {}'.format(member.first_name)
    del database
    if answer:  # Если ответ не пустой
        bot.reply_to(message, answer)  # То отправляем ответ
    # Держим Дэ'Макса в курсе происходящего
    person = message.new_chat_members[0]
    bot.send_message(381279599, '{} ({}) [{}] теперь в {}'.format(person.first_name, person.username, person.id,
                                                                  message.chat.title))
    print('{} ({}) [{}] теперь в {}'.format(person.first_name, person.username, person.id, message.chat.title))


@bot.message_handler(content_types=['left_chat_member'])
def left_member(message):
    """Комментирует уход участника и прощается участником"""
    if not in_mf(message):
        return None
    person = message.left_chat_member
    if message.from_user.id == person.id:  # Чел вышел самостоятельно
        bot.reply_to(message, "Минус чувачок")
        try:
            bot.send_message(message.from_user.id, 'До встречи в @MultiFandomRu!')
        except Exception as e:
            if 'initiate conversation with a user' in str(e):
                bot.reply_to(message, "Этот чел не написал мне в личку...")
            elif 'bot was blocked by the user' in str(e):
                bot.reply_to(message, "Он меня забанил, лол")
            else:
                error(message, e)
    else:  # Чела забанили
        bot.send_video(message.chat.id, "BAADAgADhgMAAgYqMUvW-ezcbZS2ohYE")
    # Держим Дэ'Макса в курсе происходящего
    bot.send_message(381279599, '{} ({}) [{}] теперь не в {}'.format(person.first_name, person.username, person.id,
                                                                     message.chat.title))
    print('{} ({}) [{}] теперь не в {}'.format(person.first_name, person.username, person.id, message.chat.title))
