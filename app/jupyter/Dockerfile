FROM jupyter/scipy-notebook

ENV JUPYTER_PASSWORD='argon2'

# Устанавливаем Python SDK для работы с MinIO
RUN pip install minio

# Копируем скрипт для загрузки файлов из MinIO
COPY ./download_minio_files.py /usr/local/bin/download_minio_files.py

# Команда для запуска Jupyter с загрузкой файлов
CMD python /usr/local/bin/download_minio_files.py && start-notebook.sh
