from fastapi import APIRouter, HTTPException
from app.schemas import UserCreate, UserOut, JournalEntryCreate, JournalEntryOut, HealthServiceCreate, HealthServiceOut
from prisma import Prisma

router = APIRouter()



from app.db import db  
# ---------------------
# User Endpoints
# ---------------------

@router.post("/users", response_model=UserOut)
async def create_user(user: UserCreate):
    existing = await db.user.find_unique(where={"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = await db.user.create(
        data={
            "name": user.name,
            "email": user.email
        }
    )
    return new_user

@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: str):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ---------------------
# Journal Entry Endpoints
# ---------------------

@router.post("/journal", response_model=JournalEntryOut)
async def create_journal(journal: JournalEntryCreate):
    # Ensure user exists
    user = await db.user.find_unique(where={"id": journal.userId})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = journal.model_dump()

    # ✅ Convert date to full ISO 8601 DateTime string
    data["entryDate"] = data["entryDate"].isoformat() + "T00:00:00.000Z"

    # ✅ Fix: Prisma relation requires nested `connect`
    data["user"] = {"connect": {"id": journal.userId}}

    # Remove userId from data (because Prisma uses the relation)
    del data["userId"]

    new_journal = await db.journalentry.create(data=data)
    return new_journal


@router.get("/journal/{user_id}", response_model=list[JournalEntryOut])
async def get_journal_entries(user_id: str):
    journals = await db.journalentry.find_many(where={"userId": user_id})
    return journals

# ---------------------
# Health Service Endpoints
# ---------------------

@router.post("/services", response_model=HealthServiceOut)
async def create_health_service(service: HealthServiceCreate):
    new_service = await db.healthservice.create(
        data={
            "name": service.name,
            "type": service.type,
            "address": service.address,
            "latitude": service.latitude,
            "longitude": service.longitude,
        }
    )
    return new_service

@router.get("/services", response_model=list[HealthServiceOut])
async def list_health_services():
    services = await db.healthservice.find_many()
    return services
