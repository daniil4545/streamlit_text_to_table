from pathlib import Path

from .config import Config
from .logger import Logger


class ValidationError(Exception):
    """
    Исключение, выбрасываемое при ошибках валидации файла.
    """
    pass


class DataValidator:
    """
    Класс для проверки корректности входного файла перед загрузкой:
      - расширение файла
      - размер файла
      - непустой файл
    """

    def __init__(self, config: Config):
        """
        Args:
            config (Config): Объект с настройками (допустимые расширения, максимальный размер и т.д.)
        """
        self.config = config
        # Получаем логгер для данного класса
        self.logger = Logger.get(self.__class__.__name__)


    def validate_extension(self, path: Path) -> None:
        """
        Проверяет, что расширение файла соответствует разрешённым.

        Args:
            path (Path): Путь к файлу.

        Raises:
            ValidationError: если расширение не входит в allowed_ext.
        """
        ext = path.suffix.lower()

        if ext not in self.config.allowed_ext:
            msg = f"Недопустимый формат файла: {path.name}, ожидаются {self.config.allowed_ext}"
            self.logger.error(msg)
            raise ValidationError(msg)
        self.logger.info(f"Расширение {ext} валидно.")


    def validate_size(self, path: Path) -> None:
        """
        Проверяет, что размер файла не превышает максимально допустимый.

        Args:
            path (Path): Путь к файлу.

        Raises:
            ValidationError: если файл слишком большой.
        """
        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > self.config.max_file_size_mb:
            msg = (
                f"Файл слишком большой: {size_mb:.2f} MB, "
                f"максимум {self.config.max_file_size_mb} MB"
            )
            self.logger.error(msg)
            raise ValidationError(msg)
        self.logger.info(f"Размер файла {size_mb:.2f} MB в пределах допустимого.")


    def validate_not_empty(self, path: Path) -> None:
        """
        Проверяет, что файл не пуст.

        Args:
            path (Path): Путь к файлу.

        Raises:
            ValidationError: если файл пуст или содержит только пустые строки.
        """
        # Читаем первые несколько байт для проверки непустого файла
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip():
                    self.logger.info("Файл не пуст и содержит данные.")
                    return
        msg = f"Файл {path.name} пуст или не содержит данных."
        self.logger.error(msg)
        raise ValidationError(msg)


    def validate(self, path: Path) -> None:
        """
        Общая валидация файла: последовательный вызов всех проверок.

        Args:
            path (Path): Путь к файлу.

        Raises:
            ValidationError: при любой неуспешной проверке.
        """
        self.logger.info(f"Начало валидации файла: {path.name}")
        self.validate_extension(path)
        self.validate_size(path)
        self.validate_not_empty(path)
        self.logger.info(f"Файл {path.name} успешно прошёл валидацию.")
