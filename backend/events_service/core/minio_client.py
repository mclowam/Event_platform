import aioboto3

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password123"
MINIO_BUCKET = "events-photos"

session_minio = aioboto3.Session()