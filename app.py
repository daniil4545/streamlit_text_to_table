import streamlit as st

from src.config import Config
from src.logger import Logger
from src.file_manager import FileManager, FileManagerError
from src.data_validator import DataValidator, ValidationError
from src.data_loader import DataLoader, DataLoaderError


def main():
    # Инициализация конфигурации и логера
    config = Config()
    logger = Logger.get("StreamlitApp")

    st.set_page_config(page_title="Таблица из текстового файла", layout="wide")
    st.title("Отображение данных из последнего текстового файла")

    try:
        # Получаем список и выбираем последний файл
        file_manager = FileManager(config)
        files = file_manager.list_files()
        latest_file = file_manager.pick_latest(files)

        # Валидация выбранного файла
        validator = DataValidator(config)
        validator.validate(latest_file)

        # Загрузка данных в DataFrame
        loader = DataLoader(config)
        df = loader.load_dataframe(latest_file)

        # Отображение и редактирование данных в Streamlit
        st.markdown(f"**Загружен файл:** `{latest_file.name}`")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        if st.button("Сохранить изменения в файл"):
            try:
                # Сохраняем только для текстовых файлов (csv, txt)
                if latest_file.suffix.lower() in [".csv", ".txt"]:
                    edited_df.to_csv(latest_file, index=False, encoding="utf-8")
                elif latest_file.suffix.lower() in [".xls", ".xlsx"]:
                    edited_df.to_excel(latest_file, index=False)
                st.success("Изменения успешно сохранены!")
                
                logger.info(f"Файл {latest_file.name} был изменён через data_editor.")
            except Exception as e:
                st.error(f"Ошибка при сохранении файла: {e}")
                logger.error(f"Ошибка при сохранении файла {latest_file.name}: {e}")

    except FileManagerError as e:
        logger.error(f"File manager error: {e}")
        st.error(f"Ошибка работы с файлами: {e}")
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        st.error(f"Ошибка валидации файла: {e}")
    except DataLoaderError as e:
        logger.error(f"Data loading error: {e}")
        st.error(f"Ошибка загрузки данных: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        st.error(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
