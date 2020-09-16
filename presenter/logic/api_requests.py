from presenter.config.token_manager import BOT
from presenter.config.log import Logger
import requests

LOG = Logger(0) # int code for log_to_both

def request_file(file_id, save_as):
	file_info = BOT.get_file(file_id)
	req = requests.get("https://api.telegram.org/file/bot{0}/{1}".format(BOT.token, file_info.file_path))
	file_out = open("input+"+file_info.file_path, "w")
	lines = req.content()
	file_out.write(lines)
	req.close()
	file_out.close()
