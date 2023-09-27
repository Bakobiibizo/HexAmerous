import loguru
from typing import Dict

logger = loguru.logger


class Log:
    def __init__(self, level=Optional[str]="DEBUG"):
        self.logger = loguru.logger
        self.level = level
        self.logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")
        self.logger.level(self.level)
        self.map = {
            "info": self.logger.info,
            "debug": self.logger.debug,
            "warning": self.logger.warning,
            "error": self.logger.error,
            "critical": self.logger.critical,
            "exception": self.logger.exception            
        }
        
    def debug(variable_dict: Dict[str, str])-> None:
        log_str = "\n".join(f"{key} - {value}" for key, value in variable_dict.items())
        logger.debug(f"\n{log_str}\n")
        
    def info(self, values: str)-> None:
        self.logger.info(values)
    
    def warning(self, values: Optional[Union[str, List[str]]])-> None:
        if value(str):
        value_dict = self.construct_variable_dict(values)
        self.logger.warning(value_dict)
        
    def error(self, values: str)-> None:
        value_dict = self.construct_variable_dict(values)
        self.logger.error(value_dict)
        
    def critical(self, values: str)-> None:
        value_dict = self.construct_variable_dict(values)
        self.logger.critical(value_dict)
        
    def exception(self, values: str)-> None:
        value_dict = self.construct_variable_dict(values)
        self.logger.exception(value_dict)

    def construct_variable_dict(values: str) -> Dict[str, str]:
        key = ""
        keys = [key for value in values]
        variable_dict = {}
        variable_dict = {keys[value]: value for key, value in values.items()}
        return variable_dict

        
    def log(self, value: Optional[Union[str],List[str]])->None:
        if value.isinstance(str):
            self.info(value)
        else:
            self.debug(value)
 

def get_logger():
    log = Log()
    return log

if __name__ == '__main__':
    construct_variable_dict("key1", "key2")