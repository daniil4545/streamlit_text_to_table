import os
import io
import time
import pytest
import pandas as pd
from pathlib import Path

from src.config import Config
from src.file_manager import FileManager, FileManagerError
from src.data_validator import DataValidator, ValidationError
from src.data_loader import DataLoader, DataLoaderError


def test_config_defaults():
    """
    Проверка значений по умолчанию в Config.
    """
    cfg = Config()
    assert isinstance(cfg.data_dir, Path)
    assert cfg.max_file_size_mb == 50.0
    assert ".csv" in cfg.allowed_ext and ".txt" in cfg.allowed_ext
    assert isinstance(cfg.encoding_detect_bytes, int)


def test_file_manager(tmp_path):
    """
    Проверяем list_files и pick_latest на временной директории.
    """
    # создаём тестовую директорию
    cfg = Config(data_dir=tmp_path)
    fm = FileManager(cfg)

    # создаём два файла с нужным расширением
    f1 = tmp_path / "old.csv"
    f1.write_text("a,b,c\n1,2,3")
    # ждем, чтобы модификация отличалась
    time.sleep(0.1)
    f2 = tmp_path / "new.csv"
    f2.write_text("x,y,z\n4,5,6")

    files = fm.list_files()
    assert set(files) == {f1, f2}

    latest = fm.pick_latest(files)
    assert latest.name == f2.name

    # проверяем ошибку при пустом списке
    with pytest.raises(FileManagerError):
        fm.pick_latest([])


def test_data_validator(tmp_path):
    """
    Проверяем DataValidator на разных сценариях.
    """
    cfg = Config(data_dir=tmp_path, max_file_size_mb=0.001)  # очень маленький размер
    dv = DataValidator(cfg)

    # 1) недопустимое расширение
    bad = tmp_path / "file.unsupported"
    bad.write_text("test")
    with pytest.raises(ValidationError):
        dv.validate_extension(bad)

    # 2) слишком большой файл
    big = tmp_path / "big.csv"
    # пишем >1KB (~0.001 MB)
    big.write_bytes(b"0" * 2048)
    with pytest.raises(ValidationError):
        dv.validate_size(big)

    # 3) пустой файл
    empty = tmp_path / "empty.csv"
    empty.write_text("   \n   \n")
    with pytest.raises(ValidationError):
        dv.validate_not_empty(empty)

    # 4) успешная валидация
    good = tmp_path / "good.csv"
    good.write_text("col1,col2\n1,2")
    # увеличим лимит
    cfg.max_file_size_mb = 1.0
    # не должно выбрасывать
    dv.validate(good)


def test_data_loader(tmp_path):
    """
    Проверка загрузки CSV и TXT через DataLoader.
    """
    cfg = Config(data_dir=tmp_path)
    dl = DataLoader(cfg)

    # 1) CSV файл с запятой
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b,c\n1,2,3\n4,5,6")
    df_csv = dl.load_dataframe(csv_file)
    assert isinstance(df_csv, pd.DataFrame)
    assert df_csv.shape == (2, 3)
    assert list(df_csv.columns) == ["a", "b", "c"]

    # 2) TXT файл с табуляцией
    txt_file = tmp_path / "data.txt"
    txt_file.write_text("x\ty\tz\n7\t8\t9")
    df_txt = dl.load_dataframe(txt_file)
    assert isinstance(df_txt, pd.DataFrame)
    assert df_txt.shape == (1, 3)
    assert list(df_txt.columns) == ["x", "y", "z"]

    # 3) Ошибка при чтении несуществующего файла
    with pytest.raises(DataLoaderError):
        dl.load_dataframe(tmp_path / "nofile.csv")
