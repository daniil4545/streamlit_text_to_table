from pathlib import Path
import chardet
import csv
import pandas as pd
import itertools

from .config import Config
from .logger import Logger


class DataLoaderError(Exception):
    """
    Исключение для ошибок при загрузке данных.
    """
    pass


class DataLoader:
    """
    Класс для загрузки текстовых файлов в DataFrame:
      - определяет кодировку с помощью chardet
      - определяет разделитель, анализируя первые строки
      - загружает DataFrame через pandas
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = Logger.get(self.__class__.__name__)

    def detect_encoding(self, path: Path) -> str:
        """
        Определяет кодировку файла, читая первые config.encoding_detect_bytes байт.

        Returns:
            str: название кодировки.
        """
        self.logger.info(f"Определение кодировки для файла {path.name}")
        raw = path.read_bytes()[: self.config.encoding_detect_bytes]
        result = chardet.detect(raw)
        encoding = result['encoding'] or 'utf-8'
        self.logger.info(f"Обнаруженная кодировка: {encoding}")
        
        return encoding

    def detect_separator(self, path: Path, encoding: str) -> str:
        """
        Определяет наиболее вероятный разделитель, анализируя первые нескольких строк.

        Args:
            path (Path): путь к файлу
            encoding (str): кодировка файла

        Returns:
            str: символ разделителя
        """
        self.logger.info(f"Определение разделителя для файла {path.name}")
        with path.open('r', encoding=encoding, errors='ignore') as f:
            sample = ''.join(itertools.islice(f, 5))
        # Возможные разделители
        delimiters = [',', '\t', ';', '|']
        # Считаем, какой разделитель встречается чаще всего в образце
        counts = {d: sample.count(d) for d in delimiters}
        sep = max(counts, key=counts.get)
        self.logger.info(f"Выбран разделитель: '{sep}' (counts={counts})")
        return sep

    def load_dataframe(self, path: Path) -> pd.DataFrame:
        """
        Загружает файл в pandas.DataFrame после определения кодировки и разделителя.

        Args:
            path (Path): путь к файлу

        Returns:
            pd.DataFrame: загруженные данные.

        Raises:
            DataLoaderError: в случае ошибок чтения.
        """
        ext = path.suffix.lower()
        try:
            if ext not in self.config.allowed_ext:
                raise DataLoaderError(f"Недопустимое расширение файла: {ext}")
            
            if ext in [".csv", ".txt"]:
                self.logger.info(f"Загрузка текстового файла {path.name}")
                encoding = self.detect_encoding(path)
                sep = self.detect_separator(path, encoding)
                df = pd.read_csv(path, sep=sep, encoding=encoding)

            elif ext in [".xls", ".xlsx"]:
                self.logger.info(f"Загрузка Excel-файла {path.name}")
                df = pd.read_excel(path)

            else:
                raise DataLoaderError(f"Для расширения {ext} нет метода открытия")

            self.logger.info(f"Успешно загружено {len(df)} строк и {len(df.columns)} столбцов.")
            return df

        except Exception as e:
            msg = f"Ошибка при загрузке данных из {path.name}: {e}"
            self.logger.error(msg)
            raise DataLoaderError(msg) from e
