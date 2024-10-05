import os
from loguru import logger
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Logger:
    def __init__(self, level: str = "INFO"):
        self.logger = logger
        self.level = level

    def log(self, message: str, level: Optional[str] = None):
        if level is None:
            level = self.level
        if level == "INFO":
            self.logger.info(message)
        elif self.level == "DEBUG":
            self.logger.debug(message)
        elif self.level == "WARNING":
            self.logger.warning(message)
        elif self.level == "CRITICAL":
            self.logger.critical(message)
        elif self.level == "SUCCESS":
            self.logger.success(message)
        elif self.level == "TRACE":
            self.logger.trace(message)
        elif self.level == "EXCEPTION":
            self.logger.exception(message)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_error(self, message: str):
        self.logger.error(message)


    def log_debug(self, message: str):
        self.logger.debug(message)


    def log_warning(self, message: str):
        self.logger.warning(message)


    def log_critical(self, message: str):
        self.logger.critical(message)


    def log_success(self, message: str):
        self.logger.success(message)


    def log_trace(self, message: str):
        self.logger.trace(message)


    def log_exception(self, message: str):
        self.logger.exception(message)
        
    def get_logger(self):
        return self.logger

def get_logger(level: str = None):        
    log_level = level.upper() if level else os.getenv("LOG_LEVEL", "INFO")
    return Logger(log_level).get_logger()

if __name__ == "__main__":
    log = get_logger()
    log.info("Hello World")
