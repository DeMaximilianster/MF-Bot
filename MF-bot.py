# -*- coding: utf-8 -*-
from view.input import *
from presenter.config.token import inf_mode
from presenter.config.log import Loger, log_to

log = Loger(log_to)

if inf_mode:
    bot.infinity_polling()  # Запуск бота
else:
    try:
        #  telebot.logger.setLevel("DEBUG")  # Иногда помогает, но обычно не нужна
        bot.polling(none_stop=True)
    except Exception as e:
        log.log_print(e)

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
# TODO /top_warns
# TODO Эротические команды
