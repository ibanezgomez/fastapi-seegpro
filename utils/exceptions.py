from utils.logger import log

class CustomException(Exception):
    def __init__(self, message, original_exception, status_code):
        self.message = message
        self.original_exception = original_exception
        self.status_code = status_code

    def __str__(self):
        return self.message