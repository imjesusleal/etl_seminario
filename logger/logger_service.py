import logging
import os
import sys


class LoggerService:
    def __init__(self, log_dir="logs", log_name="app.log", also_console: bool = True):
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_name)

        self.logger = logging.getLogger("novashop_etl")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        self.logger.propagate = False

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        if also_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def info(self, mensaje):
        self.logger.info(mensaje)

    def warning(self, mensaje):
        self.logger.warning(mensaje)

    def error(self, mensaje):
        self.logger.error(mensaje)

    def exception(self, mensaje):
        self.logger.exception(mensaje)
