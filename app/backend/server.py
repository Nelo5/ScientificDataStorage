import os
import shutil
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
import pathlib
from pathlib import Path

S3_BUCKET_NAME = "scientificdata"

class FileModel(BaseModel):
    id: int
    file_name: str
    file_author: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

def initialize_database():
    """Initialize the database with required tables."""
    conn = psycopg2.connect(
        database="exampledb",
        user="docker",
        password="docker",
        host="database"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            file_name TEXT NOT NULL,
            file_author TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def initialize_s3_bucket():
    client = Minio(
        "minio:9000",
        access_key="ROOTNAME",
        secret_key="PASSWORD",
        secure=False
    )
    found = client.bucket_exists(S3_BUCKET_NAME)
    if not found:
        client.make_bucket(S3_BUCKET_NAME)
    else:
        print(f"Bucket '{S3_BUCKET_NAME}' already exists.")

@app.on_event("startup")
async def startup_event():
    print("Initializing database and S3 bucket...")
    initialize_database()
    initialize_s3_bucket()

@app.get('/status')
async def check_status():
    return "Hello world"

@app.get("/files", response_model=List[FileModel])
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
            )
        )
    cur.close()
    conn.close()
    return formatted_files

@app.post("/files", status_code=201)
async def add_file(file: UploadFile, author: str = Form(...)):
    client = Minio(
        "minio:9000",
        access_key="ROOTNAME",
        secret_key="PASSWORD",
        secure=False
    )

    client.put_object(
        S3_BUCKET_NAME,
        file.filename,
        file.file,
        length=-1,
        part_size=10*1024*1024
    )

    client.fget_object(S3_BUCKET_NAME, file.filename, f"/files/{file.filename}")

    conn = psycopg2.connect(
        database="exampledb",
        user="docker",
        password="docker",
        host="database"
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO files (file_name, file_author) VALUES (%s, %s)", (file.filename, author))
    conn.commit()
    cur.close()
    conn.close()

@app.get("/files/download/{file_name}")
async def download_file(file_name: str):
    client = Minio(
        "minio:9000",
        access_key="ROOTNAME",
        secret_key="PASSWORD",
        secure=False
    )

    try:
        response = client.get_object(S3_BUCKET_NAME, file_name)
        file_data = BytesIO(response.read())
        response.close()
        response.release_conn()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")
    
    encoded_file_name = quote(file_name)

    return StreamingResponse(
        file_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={encoded_file_name}"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
