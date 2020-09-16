"""Module with bot token and some options"""

import json
from os import path, listdir
from telebot import TeleBot

BOT_CONFIGS = None
ERROR_LOG = "UNKNOWN ERROR"
PATH = path.join('presenter', 'config', 'tokens')

if path.exists(PATH):
    # Getting all files with tokens
    file_gen = [file for file in listdir(PATH) if path.isfile(path.join(PATH, file))]
    bot_configs_dict = dict()
    for file_name in file_gen:
        with open(path.join(PATH, file_name), 'r', encoding='utf-8') as file:
            bot_configs_dict[file_name[:-5]] = json.load(file)
    if len(bot_configs_dict) == 0:
        ERROR_LOG = "Put in presenter/config/tokens jsons with format: {token: str, non_stop: bool}"
    elif len(bot_configs_dict) == 1:
        BOT_CONFIGS = list(bot_configs_dict.values())[0]
    else:
        print("Available configs: " + ", ".join(bot_configs_dict.keys()))
        BOT_CONFIGS = bot_configs_dict[input("Input configs you would like to use: ")]
else:
    ERROR_LOG = "\n1. Create a folder 'tokens' in presenter/config" \
                "\n2. Put in that folder json files with format: {token: str, non_stop: bool}"


if BOT_CONFIGS is not None:
    if BOT_CONFIGS['non_stop']:
        BOT = TeleBot(BOT_CONFIGS['token'], threaded=False, num_threads=1)
    else:
        BOT = TeleBot(BOT_CONFIGS['token'], threaded=True, num_threads=1)
else:
    raise Exception(ERROR_LOG)
