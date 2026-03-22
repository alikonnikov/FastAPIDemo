import asyncio
from app.worker.celery_app import celery_app
from app.services.ai_service import get_ai_task_suggestion
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.core.config import settings
from app.models.task import TaskSuggestion

async def process_ai_suggestion(task_id: str, text: str):
    # Setup Mongo (separate connection for worker if needed)
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]
    
    try:
        suggestion: TaskSuggestion = await get_ai_task_suggestion(text)
        
        # Update task in Mongo
        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "title": suggestion.title,
                    "description": suggestion.description,
                    "priority": suggestion.priority,
                    "tags": suggestion.tags,
                    "status": "ready"
                }
            }
        )
    except Exception as e:
        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": "error", "error_info": str(e)}}
        )
    finally:
        client.close()

@celery_app.task(name="app.worker.tasks.generate_task_suggestion")
def generate_task_suggestion(task_id: str, text: str):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # In some environments, we might need a separate loop
        new_loop = asyncio.new_event_loop()
        new_loop.run_until_complete(process_ai_suggestion(task_id, text))
    else:
        loop.run_until_complete(process_ai_suggestion(task_id, text))
