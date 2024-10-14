import logging
import logging_json
import inspect
from pytz import timezone
from utils.config import config
from starlette.middleware.base import BaseHTTPMiddleware

def getFnName():
    current_frame = inspect.currentframe()
    caller_frame = current_frame.f_back
    function_name = caller_frame.f_code.co_name
    return function_name

class Logger:
    def __init__(self):
        self.level    = None
        self.format   = None
        self.instance = None
        self.user   = None
        self.setup(level=config.log_level, format=config.log_format)

    def _getJSONLogger(self):
        log_json = logging.getLogger("sysloger")
        log_json.setLevel(self.level)
        # Log Format
        formatter = logging_json.JSONFormatter(fields={
            "time": "asctime",
            "level": "levelname",
        })
        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(self.level)
        streamhandler.setFormatter(formatter)
        log_json.addHandler(streamhandler)
        return log_json

    def _getSTDOutLogger(self):
        log_stdout = logging.getLogger("sysloger")
        log_stdout.setLevel(self.level)
        formatter = logging.Formatter("\033[0m%(asctime)s - \033[95m[user: \033[0m%(user)s\033[95m]\033[0m - \033[92m%(levelname)s\033[0m - \033[92m%(action)s\033[0m - \033[0m\033[97m%(message)s\033[0m")        
        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(self.level)
        streamhandler.setFormatter(formatter)
        log_stdout.addHandler(streamhandler)
        return log_stdout

    def _getLevelByString(self, string_level: str):
        res=logging.INFO
        if string_level in ["DEBUG", "ERROR"]:
            if    string_level == "DEBUG": res=logging.DEBUG
            else: res=logging.ERROR
        return res

    def setUser(self, user: str):
        self.user=user


    def setup(self, format: str = None, level: str = None):
        if format != None: 
            self.format=format
        if level  != None: 
            self.level=self._getLevelByString(level)
        if self.instance!=None: self.clear_handlers()
        self.instance = self._getLogger()

    def clear_handlers(self):
        for handler in self.instance.handlers[:]:
            self.instance.removeHandler(handler)

    def _getLogger(self):
        if self.format == 'json':
            return self._getJSONLogger()
        else:
            return self._getSTDOutLogger()

    def _handle_log_record(self, level, message, user=None, action=None):
        if self.format == 'string': 
            streamhandler = logging.StreamHandler()
            if level == logging.ERROR:
                formatter = logging.Formatter("\033[0m%(asctime)s - \033[95m[user: \033[0m%(user)s\033[95m]\033[0m - \033[91m%(levelname)s\033[0m - \033[92m%(action)s\033[0m - \033[0m\033[97m%(message)s\033[0m")
            elif level == logging.DEBUG:
                formatter = logging.Formatter("\033[0m%(asctime)s - \033[95m[user: \033[0m%(user)s\033[95m]\033[0m - \033[93m%(levelname)s\033[0m - \033[92m%(action)s\033[0m - \033[0m\033[97m%(message)s\033[0m")
            else: #INFO
                formatter = logging.Formatter("\033[0m%(asctime)s - \033[95m[user: \033[0m%(user)s\033[95m]\033[0m - \033[92m%(levelname)s\033[0m - \033[92m%(action)s\033[0m - \033[0m\033[97m%(message)s\033[0m")
            self.clear_handlers()
            streamhandler.setFormatter(formatter)
            self.instance.addHandler(streamhandler)
       
        log_record = self.instance.makeRecord(
            self.instance.name,
            level,
            "",
            0,
            message,
            None,
            None
        )
        if user!=None: log_record.user = user
        else: log_record.user = self.user
    
        log_record.action = action

        self.instance.handle(log_record)

    def debug(self, message, user=None, action=None):
        self._handle_log_record(logging.DEBUG, message, user, action)

    def info(self, message, user=None, action=None):
        self._handle_log_record(logging.INFO, message, user, action)

    def error(self, message, user=None, action=None):
        self._handle_log_record(logging.ERROR, message, user, action)

log = Logger()
