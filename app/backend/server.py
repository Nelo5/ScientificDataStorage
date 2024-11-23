import boto3
import psycopg2
import uvicorn
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile
from minio import Minio


S3_BUCKET_NAME = "scientificdata"

class PhotoModel(BaseModel):
    id: int
    photo_name: str
    photo_url: str
    is_deleted: bool

app = FastAPI()

@app.get('/status')
async def check_status():
    return "Hello word"

@app.get("/photos", response_model = List[PhotoModel])
async def get_all_photos():
    conn = psycopg2.connect(
        database="exampledb", 
        user="docker",
        password="docker",
        host="database"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM photo ORDER BY id DESC")
    rows = cur.fetchall()

    formatted_photos = []
    for row in rows:
        formatted_photos.append(
            PhotoModel(
                id=row[0],
                photo_name=row[1],
                photo_url=row[2],
                is_deleted=row[3]
            )
        )
    cur.close()
    conn.close()
    return formatted_photos

@app.post("/photos", status_code=201)
async def add_photo(file: UploadFile):

    print("Create endpoint hit!!!")
    print(file.filename)
    print(file.content_type)

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
    # s3 = boto3.resource('s3',
    #                 endpoint_url='http://localhost:9000',
    #                 aws_access_key_id='hz3VAM0BzGf9lBBZ2pCl',
    #                 aws_secret_access_key='xXD7t7iLowhrCO0GjDEjw2jnI0wM6KMqUi5eDXgT')
    # bucket = s3.Bucket(S3_BUCKET_NAME)
    # bucket.upload_fileobj(file.file, file.filename, ExtraArgs={"ACL":"public-read"})

    uploaded_file_url = f"http://{'minio'}:9000/{S3_BUCKET_NAME}/{file.filename}"
    conn = psycopg2.connect(
        database="exampledb", 
        user="docker",
        password="docker",
        host="database"
    )
    cur = conn.cursor()
    cur.execute(f"INSERT INTO photo (photo_name, photo_url, is_deleted) VALUES ('{file.filename}', '{uploaded_file_url}', 0)")
    conn.commit()
    cur.close()
    conn.close()
''