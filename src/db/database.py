import motor.motor_asyncio
from beanie import init_beanie

from src.db.config import settings
from src.db.models import Bludv


async def init():
    # Create Motor client

    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)

    # Init beanie with the Product document class
    await init_beanie(database=client.streamio, document_models=[Bludv])
