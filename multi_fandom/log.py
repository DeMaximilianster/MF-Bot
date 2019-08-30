import time
LOG_TO_FILE = 1
LOG_TO_CONSOLE = 2
LOG_BOTH = 0
class Loger:
    LOG_FILES = []
    method = 2
    def __init__(self, default_log_method = 2):
        self.method = default_log_method
    def logPrint(self, *args):
        if self.method%2 == 0:
            timeNow = time.gmtime(int(time.time()))
            for arg in args:
                print("[{}] {}".format("{}.{}.{}|{}:{}:{}".format(timeNow[2], 
                timeNow[1], timeNow[0], timeNow[3], timeNow[4], timeNow[5]), arg))
        if self.method == 0 or self.method == 1:
            for fname in self.LOG_FILES:
                with open(fname, 'a+') as logFile:
                    for arg in args:
                        logFile.write("[{}] {}".format("{}.{}.{}|{}:{}:{}".format(timeNow[2], 
                        timeNow[1], timeNow[0], timeNow[3], timeNow[4], timeNow[5]), arg))
    def addLogFile(self, fname):
        self.LOG_FILES.append(fname)
        
                    
