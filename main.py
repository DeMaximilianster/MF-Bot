# -*- coding: utf-8 -*-
"""Main programm in the code. Run it"""
#  from requests import ReadTimeout, ConnectionError
#  from urllib3.exceptions import NewConnectionError, MaxRetryError, ReadTimeoutError
import view.input
from presenter.config.token import INFINITE_MODE, BOT
from presenter.config.config_func import update_old_systems_json

print(view.input.WORK)

update_old_systems_json()
if INFINITE_MODE:
    while True:
        try:
            BOT.send_message(381279599, "Приступаю к работе в бесконечном режиме, босс!")
            BOT.infinity_polling()  # Запуск бота
        except Exception as e:
            BOT.send_message(381279599, "Меня подкосило исключение:\n\n"+str(e))
else:
    #  telebot.logger.setLevel("DEBUG")  # Иногда помогает, но обычно не нужна
    try:
        BOT.send_message(381279599, "Приступаю к работе, босс!")
        BOT.polling(none_stop=True)
    except Exception as e:
        BOT.send_message(381279599, "Меня подкосило исключение:\n\n" + str(e))

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
# TODO при использовании команды /messages бот должен включать функцию update_person или как она там называется
# TODO добавить в counter инкремент главного счётчика сообщений
# TODO Слежение за юзеркой и ником чела. Хранить всю историю и время обнаружения изменений
