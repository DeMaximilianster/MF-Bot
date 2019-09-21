import time
LOG_TO_FILE = 1  # Записать только в файл
LOG_TO_CONSOLE = 2  # Записать только в консоль
LOG_BOTH = 0  # Записать и в файл, и в консоль


class Loger:
    LOG_FILES = []
    method = 2

    def __init__(self, default_log_method=2):
        self.method = default_log_method

    def log_print(self, *args):
        time_now = time.gmtime(int(time.time()))  # Время записи лога
        if self.method % 2 == 0:  # Запись в консоль
            for arg in args:
                print("[{}] {}".format("{}.{}.{}|{}:{}:{}".format(time_now[2],
                      time_now[1], time_now[0], time_now[3], time_now[4], time_now[5]), arg))
        if self.method <= 1:  # Запись в файл
            for fname in self.LOG_FILES:
                with open(fname, 'a+') as logFile:
                    for arg in args:
                        logFile.write("[{}] {}".format("{}.{}.{}|{}:{}:{}".format(time_now[2],
                                      time_now[1], time_now[0], time_now[3], time_now[4], time_now[5]), arg))

    def add_log_file(self, fname):
        self.LOG_FILES.append(fname)
