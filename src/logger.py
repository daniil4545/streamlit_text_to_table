import logging
from logging import Logger as _Logger

class Logger:
    """
    Класс для настройки логирования
    """
    @staticmethod
    def get(name: str) -> _Logger:
        """
        Возвращает экземпляр логгера
        """
        logger = logging.getLogger(name)

        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # Консольный хэндлер
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)

            # Файловый хэндлер
            fh = logging.FileHandler("app.log", encoding="utf-8")
            fh.setLevel(logging.INFO)
  
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            ch.setFormatter(formatter)
            fh.setFormatter(formatter)

            logger.addHandler(ch)
            logger.addHandler(fh)
        return logger
