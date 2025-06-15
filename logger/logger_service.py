import logging
import os

class LoggerService:
    def __init__(self, log_dir='logs', log_name='app.log'):
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, log_name)

        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.logger = logging.getLogger()

    def info(self, mensaje):
        self.logger.info(mensaje)

    def warning(self, mensaje):
        self.logger.warning(mensaje)

    def error(self, mensaje):
        self.logger.error(mensaje)

    def exception(self, mensaje):
        self.logger.exception(mensaje) 