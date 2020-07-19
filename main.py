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
