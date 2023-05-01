```python
import logging
from logging.handlers import TimedRotatingFileHandler
import os

class YeLoggerOfYor(object):
    def __init__(self, log_file_name):
        self.log_file_name = log_file_name
        self.logger = logging.getLogger(__name__)

        # set the log level
        self.logger.setLevel(logging.INFO)

        # add a timed rotating file handler to the logger
        self.file_handler = TimedRotatingFileHandler(self.log_file_name, when='midnight', backupCount=7)
        self.file_handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line %(lineno)d')
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

def get_logger(log_file_name):
    my_logger = YeLoggerOfYor(log_file_name)
    return my_logger.logger
```
