# -*- coding: utf-8 -*-
"""Main programm in the code. Run it"""
#  from requests import ReadTimeout, ConnectionError
#  from urllib3.exceptions import NewConnectionError, MaxRetryError, ReadTimeoutError
import view.input
from presenter.config.token import INFINITE_MODE, BOT
from presenter.config.config_var import CREATOR_ID
from presenter.config.config_func import update_old_systems_json

print(view.input.WORK)

update_old_systems_json()
if INFINITE_MODE:
    BOT.send_message(CREATOR_ID, "Приступаю к работе в бесконечном режиме, босс!")
    BOT.infinity_polling()  # Запуск бота
else:
    #  telebot.logger.setLevel("DEBUG")  # Иногда помогает, но обычно не нужна
    BOT.send_message(CREATOR_ID, "Приступаю к работе, босс!")
    BOT.polling(none_stop=True)

# TODO провокацио-голосовашки и оск-голосовашки
# TODO Антифлуд механизм
# TODO Менеджмент директив
# TODO Менеджмент идей для голосовашек
# TODO Менеджмент учёта голосовашек
# TODO Поменять разметку Markdown на HTML, где это уместно
# TODO Доска почёта
# TODO Англоязычная локализация бота
# TODO Команда для прайс-листа
# TODO Команда /twink
# TODO БЛЯТЬ ОБНОВИТЬ ЭТУ ЕБАННУЮ ССАННУЮ ТАБЛИЦУ ДАТАБЕЙЗ.ТХТ
# TODO Тэги в хранилище
# TODO Панелька для выключения/включения тех или иных уведомлений в админском чате
# TODO Апгрейд хранилища до возможности организовать цитатник
# TODO при использовании команды /messages бот должен включать функцию
#  update_person или как она там называется
# TODO добавить в counter инкремент главного счётчика сообщений
# TODO Слежение за юзеркой и ником чела. Хранить всю историю и время обнаружения изменений
# TODO auto-deleting vulgar content
# TODO merging two databases files (https://t.me/MFCoding/42592)
# TODO feedback in /anon (so admins can reply to people's messages)
# TODO add captcha_completed column in members and usage of it
#  if user completed captcha once, bot won't give captcha to this person anymore
#  also create a developer command /reset_captcha so bot will captcha this person once
# TODO update channels database so bot won't ban and promote in "Polls and Directives"
#  and other channels by accident
