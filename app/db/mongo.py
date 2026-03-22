from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDB()

async def connect_to_mongo():
    db_instance.client = AsyncIOMotorClient(settings.MONGO_URL)
    db_instance.db = db_instance.client[settings.MONGO_DB]
    
    await db_instance.db.users.create_index("username", unique=True)
    await db_instance.db.users.create_index("email", unique=True)
    await db_instance.db.tasks.create_index("user_id")

async def close_mongo_connection():
    db_instance.client.close()

def get_database():
    return db_instance.db
