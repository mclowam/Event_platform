from core.minio_client import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    session_minio,
)


class MinioImageStorage:
    async def upload(self, file_obj, key: str) -> None:
        async with session_minio.client(
                "s3",
                endpoint_url=MINIO_ENDPOINT,
                aws_access_key_id=MINIO_ACCESS_KEY,
                aws_secret_access_key=MINIO_SECRET_KEY,
        ) as s3:
            await s3.upload_fileobj(file_obj, MINIO_BUCKET, key)

    async def get_bytes(self, key: str) -> tuple[bytes, str]:
        async with session_minio.client(
                "s3",
                endpoint_url=MINIO_ENDPOINT,
                aws_access_key_id=MINIO_ACCESS_KEY,
                aws_secret_access_key=MINIO_SECRET_KEY,
        ) as s3:
            response = await s3.get_object(Bucket=MINIO_BUCKET, Key=key)
            data = await response["Body"].read()
            content_type = response.get("ContentType", "image/jpeg")
            return data, content_type
