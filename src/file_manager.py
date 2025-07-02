from pathlib import Path
from typing import List

from .config import Config
from .logger import Logger


class FileManagerError(Exception):
    """
    Исключение для ошибок при работе с файловым менеджером.
    """
    pass


class FileManager:
    """
    Класс для управления файлами в директории:
      - перечисляет файлы с подходящими расширениями
      - выбирает самый новый файл по дате модификации
    """

    def __init__(self, config: Config):
        """
        Args:
            config (Config): объект с настройками (директория, разрешенные расширения)
        """
        self.config = config
        self.logger = Logger.get(self.__class__.__name__)

    def list_files(self) -> List[Path]:
        """
        Перечисляет все файлы в директории config.data_dir с допустимыми расширениями.

        Returns:
            List[Path]: список путей к файлам.

        Raises:
            FileManagerError: если директория не существует или недоступна.
        """
        data_dir = Path(self.config.data_dir)
        if not data_dir.exists() or not data_dir.is_dir():
            msg = f"Директория {data_dir} не найдена или недоступна."
            self.logger.error(msg)
            raise FileManagerError(msg)

        # Получаем все файлы с разрешенными расширениями
        files = []
        for ext in self.config.allowed_ext:
            files.extend(data_dir.glob(f"*{ext}"))

        # Логируем найденные файлы
        self.logger.info(f"Найдено {len(files)} файлов с расширениями {self.config.allowed_ext}.")
        return files

    def pick_latest(self, files: List[Path]) -> Path:
        """
        Выбирает файл с самой новой датой модификации.

        Args:
            files (List[Path]): список файлов для выбора.

        Returns:
            Path: путь к самому свежему файлу.

        Raises:
            FileManagerError: если список пуст.
        """
        if not files:
            msg = "Нет файлов для выбора."
            self.logger.error(msg)
            raise FileManagerError(msg)

        # Находим файл с максимальным временем модификации
        latest = max(files, key=lambda p: p.stat().st_mtime)
        mod_time = latest.stat().st_mtime
        self.logger.info(f"Самый новый файл: {latest.name}, время модификации: {mod_time}.")
        return latest
