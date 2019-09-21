# -*- coding: utf-8 -*-
from presenter.config.config_func import Database, time_replace, error
from view.output import delete, kick, send, promote, reply, send_video


def deleter(message):
    """Удаляет медиа ночью"""
    database = Database()
    # Получаем из БД переменную, отвечающую за работу это функции
    delete_mode = database.get('delete', 'config', 'var')[1]
    del database
    if not delete_mode:
        return None
    if time_replace(message.date)[1] >= 22 or time_replace(message.date)[1] < 8:  # Время, когда надо удалять
        database = Database()
        rank = database.get(message.from_user.id)[3]
        if rank == 'Гость' or rank == 'Кто-то':
            # TODO бот делает это предупреждение не чаще раза в 24 часа на человека

            #  ans = "Э, нет, в такое время медиа нельзя присылать гостям чата. "
            #  ans += "Если вы не гость, то обратитесь к Дэ'Максу"
            #  bot.send_message(message.chat.id, ans)
            delete(message.chat.id, message.message_id)


def new_member(message):
    """Реагирует на вход в чат"""
    database = Database()
    member = message.new_chat_members[0]
    answer = ''
    rank = database.get(member.id)[3]  # Получаем его звание
    if member.is_bot:
        send(message.chat.id, "Ещё один бот, вряд-ли более умный, чем я")
    if rank == "Нарушитель":
        kick(message.chat.id, member.id)
    elif rank == "Админ" or rank == "Член Комитета":
        promote(message.chat.id, member.id,
                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
        answer += "О, добро пожаловать, держи админку"
    elif rank == "Заместитель":
        promote(message.chat.id, member.id,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=True)
        answer += "О, добро пожаловать, держи полную админку"
    else:  # У нового участника нет особенностей
        answer = 'Добро пожаловать, {}'.format(member.first_name)
    del database
    if answer:  # Если ответ не пустой
        reply(message, answer)  # То отправляем ответ
    # Держим Дэ'Макса в курсе происходящего
    person = message.new_chat_members[0]
    send(381279599, '{} (@{}) [{}] теперь в {}'.format(person.first_name, person.username, person.id,
                                                       message.chat.title))
    print('{} ({}) [{}] теперь в {}'.format(person.first_name, person.username, person.id, message.chat.title))


def left_member(message):
    """Комментирует уход участника и прощается участником"""
    person = message.left_chat_member
    if message.from_user.id == person.id:  # Чел вышел самостоятельно
        reply(message, "Минус чувачок")
        try:
            send(message.from_user.id, 'До встречи в @MultiFandomRu!')
        except Exception as e:
            if 'initiate conversation with a user' in str(e):
                reply(message, "Этот чел не написал мне в личку...")
            elif 'bot was blocked by the user' in str(e):
                reply(message, "Он меня забанил, лол")
            else:
                error(message, e)
    else:  # Чела забанили
        send_video(message.chat.id, "BAADAgADhgMAAgYqMUvW-ezcbZS2ohYE")
    # Держим Дэ'Макса в курсе происходящего
    send(381279599, '{} (@{}) [{}] теперь не в {}'.format(person.first_name, person.username, person.id,
                                                          message.chat.title))
    print('{} ({}) [{}] теперь не в {}'.format(person.first_name, person.username, person.id, message.chat.title))
