from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1 import routes
from app.db import db  # ✅ Import db from the new file
from dotenv import load_dotenv
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(routes.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to HealthBridge API"}
