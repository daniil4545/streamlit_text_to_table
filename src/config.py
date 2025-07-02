from pathlib import Path
from typing import List


class Config:
    """
    Настройки конфигурации приложения
    """
    def __init__(
            self,
            data_dir: Path = Path("/mnt/data"),
            max_file_size_mb: float = 50.0,
            allowed_ext: List[str] = None,
            encoding_detect_bytes: int = 1000,
    ):  
        # Директория где хранится файл
        self.data_dir: Path = data_dir
        
        # Максимальный размер файла (в мб)
        self.max_file_size_mb: float = max_file_size_mb

        # Допустимые расширения файла
        self.allowed_ext: List[str] = allowed_ext or ['.csv', '.txt', ".xls", ".xlsx"]

        # Колво байт для определения кодировки
        self.encoding_detect_bytes: int = encoding_detect_bytes

    def __repr__(self) -> str:
        return (
            f"Config(data_dir={self.data_dir}, max_file_size_mb={self.max_file_size_mb}, "
            f"allowed_ext={self.allowed_ext}, encoding_detect_bytes={self.encoding_detect_bytes})"
        )