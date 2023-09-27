
from typing import Dict, Optional, Union, List
import loguru
import sys
import json

logger = loguru.logger

class Log:
    def __init__(self, level: Optional[str] = 'DEBUG'):
        self.logger = loguru.logger
        self.level = level
        self.logger.add(
            sys.stdout, 
            colorize=True, 
            format='<green>{time}</green> <level>{message}</level>'
            )
        self.logger.level(self.level)
        self.map = {
            'info': self.logger.info,
            'debug': self.logger.debug,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical,
            'exception': self.logger.exception
        }

    def debug(self, variable_dict: Optional[Union[str, Dict[str, str],
List]]) -> None:
        if isinstance(variable_dict, int):
            variable_dict = str(variable_dict)
        if isinstance(variable_dict, str):
            variable_dict = self.get_variable_dict(variable_dict)
        elif isinstance(variable_dict, list):
            variable_dict = {str(i): value for i, value in
enumerate(variable_dict)}
        log_str = '\n'.join(f'{key} - {value}' for key, value in
variable_dict.items())
        self.logger.debug(f'\n{log_str}\n')

    def info(self, values: str) -> None:
        if isinstance(values, str):
            self.logger.info(values)
        else:
            return "int value"

    def warning(self, values: Optional[Union[str, List[str]]]) -> None:
        if isinstance(values, str):
            value_dict = self.get_variable_dict(values)
            self.logger.warning(value_dict)
    def error(self, values: str) -> None:
        value_dict = self.get_variable_dict(values)
        self.logger.error(value_dict)

    def critical(self, values: str) -> None:
        value_dict = self.get_variable_dict(values)
        self.logger.critical(value_dict)

    def exception(self, values: str) -> None:
        value_dict = self.get_variable_dict(values)
        self.logger.exception(value_dict)

    def get_variable_dict(self, values: str) -> dict:
        return {char: char for char in values}

    def log(self, value: Optional[Union[str, Dict[str, str], List]]) -> None:
        if isinstance(value, int):
            self.info(str(value))
        if value is None:
            return
        if isinstance(value, str):
            self.info(value)
        elif isinstance(value, list):
            for v in value:
                self.debug(v)
        else:
            self.debug(value)

def get_logger():
    return Log()