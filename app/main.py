from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.api.auth import router as auth_router
from app.db.mongo import connect_to_mongo, close_mongo_connection

app = FastAPI(title="AI-Assisted Task Tracker")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(api_router, prefix="/api/v1", tags=["tasks"])

# Обработка OPTIONS для случаев, когда CORSMiddleware по какой-то причине пропускает запрос
@app.options("/{path:path}")
async def preflight_handler(path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Private-Network": "true",
        },
    )

@app.get("/")
async def root():
    return {"message": "Welcome to AI-Assisted Task Tracker API"}
