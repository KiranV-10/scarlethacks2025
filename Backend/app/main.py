from fastapi import FastAPI
from app.api.V1 import routes

app = FastAPI()

app.include_router(routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to HealthBridge API"}
