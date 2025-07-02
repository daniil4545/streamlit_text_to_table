#Базовый образ
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV LANG=C.UTF-8
ENV TZ=Europe/Moscow

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY src/ ./src/
COPY app.py ./

# Открываем порт
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
