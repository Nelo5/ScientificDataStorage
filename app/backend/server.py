import shutil
import boto3
import psycopg2
import uvicorn
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, Form, Response, HTTPException
from minio import Minio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO
from urllib.parse import quote
import os


S3_BUCKET_NAME = "scientificdata"

class FileModel(BaseModel):
    id: int
    file_name: str
    file_author: str
    is_deleted: bool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/status')
async def check_status():
    return "Hello word"

@app.get("/files", response_model = List[FileModel])
async def get_all_files():
    conn = psycopg2.connect(
        database="exampledb", 
        user="docker",
        password="docker",
        host="database"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM files ORDER BY id DESC")
    rows = cur.fetchall()

    formatted_files = []
    for row in rows:
        formatted_files.append(
            FileModel(
                id=row[0],
                file_name=row[1],
                file_author=row[2],
                is_deleted=row[3]
            )
        )
    cur.close()
    conn.close()
    return formatted_files

@app.post("/files", status_code=201)
async def add_file(file: UploadFile, author: str = Form(...)):



    client = Minio("minio:9000",
    access_key="hz3VAM0BzGf9lBBZ2pCl",
    secret_key="xXD7t7iLowhrCO0GjDEjw2jnI0wM6KMqUi5eDXgT",
    secure=False)

    client.put_object(
            S3_BUCKET_NAME,
            file.filename,
            file.file,
            length=-1,
            part_size=10*1024*1024)
    
    file_path = os.path.join("jupyter","data", file.filename)
    client.fget_object(S3_BUCKET_NAME, file.filename, file_path)

    conn = psycopg2.connect(
        database="exampledb", 
        user="docker",
        password="docker",
        host="database"
    )
    cur = conn.cursor()
    cur.execute(f"INSERT INTO files (file_name, file_author) VALUES ('{file.filename}', '{author}')")
    conn.commit()
    cur.close()
    conn.close()

# @app.get("/files/{file_name}")
# async def download_file(file_name: str):
#     """Downloads a file from Minio."""
#     client = Minio("minio:9000",
#                    access_key="hz3VAM0BzGf9lBBZ2pCl",
#                    secret_key="xXD7t7iLowhrCO0GjDEjw2jnI0wM6KMqUi5eDXgT",
#                    secure=False)

#     try:
#         file_data = client.get_object("scientificdata", file_name)
#         return Response(content=file_data.read(), media_type=file_data.content_type, headers={"Content-Disposition": f"attachment; filename={file_name}"})  # Set Content-Disposition for download
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=f"File '{file_name}' not found: {e}")


# Новый эндпоинт для скачивания файла
@app.get("/files/download/{file_name}")
async def download_file(file_name: str):
    # Подключение к MinIO
    client = Minio(
        "minio:9000",
        access_key="hz3VAM0BzGf9lBBZ2pCl",
        secret_key="xXD7t7iLowhrCO0GjDEjw2jnI0wM6KMqUi5eDXgT",
        secure=False
    )

    try:
        # Получение объекта из MinIO
        response = client.get_object(S3_BUCKET_NAME, file_name)
        file_data = BytesIO(response.read())
        response.close()
        response.release_conn()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")
    
    encoded_file_name = quote(file_name)

    # Возврат файла клиенту
    return StreamingResponse(
        file_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={encoded_file_name}"}
)

