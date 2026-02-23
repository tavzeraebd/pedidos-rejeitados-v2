import os
from datetime import datetime

class Logger:
    def __init__(self, log_file=None):
        if log_file is None:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'logs.log')
        self.log_file = log_file

    def clear_log(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("")

    def log(self, message, level="INFO"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{now}] [{level}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def info(self, message):
        self.log(message, level="INFO")

    def warning(self, message):
        self.log(message, level="WARNING")

    def error(self, message):
        self.log(message, level="ERROR")