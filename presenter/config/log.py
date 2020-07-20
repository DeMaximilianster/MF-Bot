"""Module for logging"""

import time
from traceback import print_exc
from io import StringIO

from presenter.config.files_paths import LOG_FILES

LOG_TO_FILE = 1  # Записать только в файл
LOG_TO_CONSOLE = 2  # Записать только в консоль
LOG_BOTH = 0  # Записать и в файл, и в консоль

LOG_TO = LOG_BOTH


class Logger:
    """Class for logging"""
    def __init__(self, log_place=2):
        self.log_place = log_place
        self.log_files = LOG_FILES
        self.gmt = 3

    def time_now(self):
        """Get time now"""
        return time.gmtime(int(time.time()) + 3600 * self.gmt)  # Время записи лога

    def log_strings(self, args):
        """Create log strings"""
        year, month, day, hour, minute, second, *_ = self.time_now()

        for arg in args:
            date = f'[{day:0>2}.{month:0>2}.{year}|{hour:0>2}:{minute:0>2}:{second:0>2}]'
            if isinstance(arg, Exception):
                temp = StringIO()
                print_exc(file=temp)
                yield f'{date} Exception detected:\n{temp.getvalue()}'
            else:
                yield f'{date} {arg}'

    def log(self, *args):
        """Print a log"""
        all_logs = '\n'.join(self.log_strings(args)) + '\n'

        if self.log_place in (0, 2):
            print(all_logs, end='')

        if self.log_place in (0, 1):
            for path in self.log_files:
                with open(path, 'a+', encoding='utf-8') as log_file:
                    log_file.write(all_logs)

    def wrap(self, func):
        """Logging wrapper around a function"""
        def wrapper(*func_args, **func_kwargs):
            self.log(func.__name__ + " invoked")
            return func(*func_args, **func_kwargs)
        return wrapper

    def add_log_file(self, path):
        """Add a log file"""
        self.log_files.append(path)
