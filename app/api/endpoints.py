from fastapi import APIRouter, HTTPException, Body, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import List
from app.models.task import Task, TaskSuggestion, TaskSuggestionInput, TaskUpdate
from app.services.ai_service import get_ai_task_suggestion
from app.db.mongo import get_database
from app.core.config import settings
from app.models.user import TokenData
from jose import JWTError, jwt
from datetime import datetime, timezone
from bson import ObjectId

from app.worker.tasks import generate_task_suggestion

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    db = get_database()
    user = await db.users.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user

@router.post("/tasks/suggest", response_model=TaskSuggestion)
async def suggest_task(input: TaskSuggestionInput, current_user: dict = Depends(get_current_user)):
    suggestion = await get_ai_task_suggestion(input.text)
    return suggestion

@router.post("/tasks/async-suggest")
async def suggest_task_async(input: TaskSuggestionInput, current_user: dict = Depends(get_current_user)):
    db = get_database()
    # Create an initial task placeholder
    new_task = {
        "title": "Processing...",
        "description": input.text,
        "status": "processing",
        "created_at": datetime.now(timezone.utc),
        "user_id": str(current_user["_id"])
    }
    result = await db.tasks.insert_one(new_task)
    task_id = str(result.inserted_id)
    
    # Send task to Celery
    generate_task_suggestion.delay(task_id, input.text)
    
    return {"task_id": task_id, "status": "processing"}

@router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskSuggestion = Body(...), current_user: dict = Depends(get_current_user)):
    db = get_database()
    new_task = task_data.model_dump()
    new_task["status"] = "ready"
    new_task["user_id"] = str(current_user["_id"])
    
    result = await db.tasks.insert_one(new_task)
    created_task = await db.tasks.find_one({"_id": result.inserted_id})
    return created_task

@router.get("/tasks", response_model=List[Task])
async def list_tasks(current_user: dict = Depends(get_current_user)):
    db = get_database()
    tasks = await db.tasks.find({"user_id": str(current_user["_id"])}).to_list(100)
    return tasks

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Optional: check if task belongs to user
    if task.get("user_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    # Check if task belongs to user
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.get("user_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await db.tasks.delete_one({"_id": ObjectId(task_id)})
    return None

@router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str, 
    task_update: TaskUpdate, 
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    # Check ownership
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.get("user_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    if update_data:
        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
    
    updated_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    return updated_task
