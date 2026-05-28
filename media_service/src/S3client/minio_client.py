import os
import json
from contextlib import AsyncExitStack
from typing import Optional
from aiobotocore.session import get_session, AioSession
from botocore.config import Config
from botocore.exceptions import ClientError


class S3Client:
    """Клиент для работы с MinIO/S3"""

    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, bucket: str):
        """
        Инициализация клиента

        Args:
            endpoint_url: URL MinIO сервера (например, http://minio:9000)
            access_key: Access Key
            secret_key: Secret Key
            bucket: Название бакета по умолчанию
        """
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket

        self._session: Optional[AioSession] = None
        self._client = None
        self._exit_stack = AsyncExitStack()

    async def start(self):
        """Запуск клиента (вызывать при старте сервиса)"""
        self._session = get_session()

        config = Config(
            max_pool_connections=50,
            connect_timeout=10,
            read_timeout=30
        )

        self._client = await self._exit_stack.enter_async_context(
            self._session.create_client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=config
            )
        )

    async def close(self):
        """Закрытие клиента (вызывать при остановке сервиса)"""
        await self._exit_stack.aclose()

    async def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """
        Создать бакет, если он не существует, и сделать его публичным.
        """
        try:
            # Проверяем существование
            await self._client.head_bucket(Bucket=bucket_name)
            return False  # Уже существует
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ('403', '404'):
                # 1. Создаём бакет
                await self._client.create_bucket(Bucket=bucket_name)

                # 2. Формируем политику публичного чтения (обязательно JSON-строка!)
                policy = json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }
                    ]
                })

                # 3. Применяем политику
                try:
                    await self._client.put_bucket_policy(
                        Bucket=bucket_name,
                        Policy=policy
                    )
                    print(f"✓ Бакет '{bucket_name}' создан и сделан публичным")
                except ClientError as policy_err:
                    # Для локальной разработки допустимо, если политика не применилась
                    print(f"⚠ Бакет '{bucket_name}' создан, но политика не применена: {policy_err}")

                return True
            raise

    async def create_buckets(self, bucket_names: list[str]):
        """Создать несколько бакетов"""
        for bucket in bucket_names:
            created = await self.create_bucket_if_not_exists(bucket)
            if created:
                print(f"✓ Бакет '{bucket}' создан")
            else:
                print(f"✓ Бакет '{bucket}' уже существует")

    async def upload_file(
            self,
            file_path: str,
            object_key: str,
            content_type: Optional[str] = None
    ) -> str:
        """
        Загрузка файла в бакет

        Args:
            file_path: Путь к локальному файлу
            object_key: Ключ объекта в бакете (например, master/track_001.flac)
            content_type: MIME тип (например, audio/flac)

        Returns:
            object_key (путь в бакете)
        """
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type

        with open(file_path, 'rb') as f:
            await self._client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=f.read(),
                **extra_args
            )

        return object_key

    def get_object_url(self, object_key: str) -> str:
        """
        Генерация постоянного URL для публичного файла

        Args:
            object_key: Ключ объекта в бакете

        Returns:
            Полный URL для доступа к файлу
        """
        base_url = self.endpoint_url.rstrip('/')
        return f"{base_url}/{self.bucket}/{object_key}"

    async def upload_bytes(
            self,
            file_bytes: bytes,
            object_key: str,
            content_type: Optional[str] = None,
            bucket: Optional[str] = None,
            **extra_kwargs
    ) -> str:
        """Загрузка байтов в бакет"""
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        extra_args.update(extra_kwargs)

        await self._client.put_object(
            Bucket=bucket or self.bucket,
            Key=object_key,
            Body=file_bytes,
            **extra_args
        )
        return object_key

    @property
    def client(self):
        return self._client
