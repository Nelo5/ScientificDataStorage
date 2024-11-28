from minio import Minio
from minio.error import S3Error
import os

BUCKET_NAME = "scientificdata"
DOWNLOAD_PATH = "/home/jovyan/work"

# Подключение к MinIO
client = Minio(
        "minio:9000",
        access_key="hz3VAM0BzGf9lBBZ2pCl",
        secret_key="xXD7t7iLowhrCO0GjDEjw2jnI0wM6KMqUi5eDXgT",
        secure=False
)

# Скачивание файлов из бакета
def download_files_from_bucket(bucket_name, download_path):
    try:
        objects = client.list_objects(bucket_name, recursive=True)
        for obj in objects:
            file_key = obj.object_name
            file_path = os.path.join(download_path, file_key)

            # Создание директорий, если их нет
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            print(f"Downloading {file_key} to {file_path}...")
            client.fget_object(bucket_name, file_key, file_path)

        print("All files downloaded successfully.")
    except S3Error as e:
        print(f"MinIO error: {e}")
    except Exception as e:
        print(f"Error downloading files: {e}")

if __name__ == "__main__":
    download_files_from_bucket(BUCKET_NAME, DOWNLOAD_PATH)
