# -*- coding: utf-8 -*-
from presenter.config.config_func import Database, time_replace
from view.output import delete, kick, send, promote, reply, send_video
from presenter.config.log import Loger, log_to

log = Loger(log_to)


def deleter(message):
    """Удаляет медиа ночью"""
    log.log_print("deleter invoked")
    database = Database()
    # Получаем из БД переменную, отвечающую за работу это функции
    delete_mode = database.get('config', ('var', 'delete'))['value']

    if not delete_mode:
        return None
    if time_replace(message.date)[1] >= 22 or time_replace(message.date)[1] < 8:  # Время, когда надо удалять
        database = Database()
        rank = database.get('members', ('id', message.from_user.id))['rank']
        if rank == 'Guest':
            # TODO бот делает это предупреждение не чаще раза в 24 часа на человека
            ans = "Э, нет, в такое время медиа нельзя присылать гостям чата. "
            ans += "Если вы не гость, то обратитесь к Дэ'Максу"
            send(message.chat.id, ans)
            delete(message.chat.id, message.message_id)


def new_member(message):
    """Реагирует на вход в чат"""
    log.log_print("new_member invoked")
    database = Database()
    member = message.new_chat_members[0]
    answer = ''

    if member.is_bot:
        send(message.chat.id, "Ещё один бот, вряд-ли более умный, чем я")
    if database.get('members', ('id', member.id), ('rank', 'Violator')):
        kick(message.chat.id, member.id)
    elif database.get('appointments', ('id', member.id), ('appointment', 'Admin')) \
            and database.get('chats', ('id', message.chat.id), ('admins_promote', 2)):
        promote(message.chat.id, member.id,
                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
        answer += "О, добро пожаловать, держи админку"
    elif database.get('members', ('id', member.id), ('rank', 'Deputy')):
        promote(message.chat.id, member.id,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=True)
        answer += "О, добро пожаловать, держи полную админку"
    else:  # У нового участника нет особенностей
        answer = 'Добро пожаловать, {}'.format(member.first_name)
    if answer:  # Если ответ не пустой
        reply(message, answer)  # То отправляем ответ
    # Держим Дэ'Макса в курсе происходящего
    person = message.new_chat_members[0]
    send(381279599, '{} (@{}) [{}] теперь в {}'.format(person.first_name, person.username, person.id,
                                                       message.chat.title))


def left_member(message):
    """Комментирует уход участника и прощается участником"""
    log.log_print("left_member invoked")
    person = message.left_chat_member
    if message.from_user.id == person.id:  # Чел вышел самостоятельно
        reply(message, "Минус чувачок")
        send(person.id, 'До встречи в @MultiFandomRu!')
    else:  # Чела забанили
        send_video(message.chat.id, "BAADAgADhgMAAgYqMUvW-ezcbZS2ohYE")
    # Держим Дэ'Макса в курсе происходящего
    send(381279599, '{} (@{}) [{}] теперь не в {}'.format(person.first_name, person.username, person.id,
                                                          message.chat.title))
