from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings
from src.utils.logger import logger


class MongoDBClient:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DATABASE]
        await self.client.admin.command("ping")
        logger.info("MongoDB connected")

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB closed")

    def get_collection(self, name: str):
        if self.db is None:
            raise RuntimeError("MongoDB is not connected")
        return self.db[name]


mongodb_client = MongoDBClient()
