from fastapi import APIRouter, HTTPException
from app.schemas import UserCreate, UserOut, JournalEntryCreate, JournalEntryOut, HealthServiceCreate, HealthServiceOut
from prisma import Prisma
import qrcode
from fastapi.responses import StreamingResponse
import io
from fastapi import HTTPException
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import HTTPException
from datetime import date
from datetime import datetime


class ProfileCreateRequest(BaseModel):
    userId: str
    gender: str
    height: int
    weight: int
    dateOfBirth: date  # Use YYYY-MM-DD format



load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print("Google API Key:", api_key)  # ✅ Debug

genai.configure(api_key=api_key)

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

@router.get("/users/{user_id}/qrcode")
async def generate_user_qr_code(user_id: str):
    # ✅ Step 1: Fetch user profile and journal data from database
    user = await db.user.find_unique(
        where={"id": user_id},
        include={
            "profile": {
                "include": {"medicalConditions": True}
            },
            "journalEntries": True
        }
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Step 2: Prepare the QR data
    qr_data = {
        "name": user.name,
        "email": user.email,
        "profile": user.profile,
        "journalEntries": user.journalEntries,
    }

    # ✅ Step 3: Convert data to JSON string (handles dates too)
    qr_text = json.dumps(qr_data, default=str)

    # ✅ Step 4: Generate QR code image
    qr_img = qrcode.make(qr_text)

    # ✅ Step 5: Convert image to byte stream
    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # ✅ Step 6: Return image as StreamingResponse
    return StreamingResponse(img_byte_arr, media_type="image/png")

@router.post("/users/{user_id}/generate-summary")
async def generate_health_summary(user_id: str):
    user = await db.user.find_unique(
        where={"id": user_id},
        include={
            "profile": {"include": {"medicalConditions": True}},
            "journalEntries": True,
        },
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = user.profile
    medical_conditions = profile.medicalConditions if profile else []
    journal_entries = user.journalEntries

    journal_summaries = "\n".join([
        f"- {entry.entryDate.strftime('%Y-%m-%d')}: {entry.entryTitle} | Medications: {entry.medicationsTaken or 'None'} | Symptoms: {entry.symptomsHad or 'None'} | Notes: {entry.otherNotes or 'None'}"
        for entry in journal_entries
    ]) if journal_entries else "No recent journal entries."

    medical_conditions_summary = ", ".join([cond.condition for cond in medical_conditions]) if medical_conditions else "None"

    prompt = f"""
User Health Summary:
- Name: {user.name}
- Email: {user.email}
- Gender: {profile.gender if profile else 'Not provided'}
- Height: {profile.height if profile else 'Not provided'} cm
- Weight: {profile.weight if profile else 'Not provided'} kg
- Date of Birth: {profile.dateOfBirth.strftime('%Y-%m-%d') if profile else 'Not provided'}
- Medical Conditions: {medical_conditions_summary}
- Recent Journal Entries:
{journal_summaries}

Based on the above data, provide:
1. A concise health summary.
2. Any health improvement suggestions.
3. Questions the user should ask a doctor.
"""

    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)

    ai_summary = response.text

    return {"summary": ai_summary}

@router.post("/profiles")
async def create_profile(profile_data: ProfileCreateRequest):
    # ✅ Check if user exists
    user = await db.user.find_unique(where={"id": profile_data.userId})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Check if profile already exists
    existing_profile = await db.profile.find_unique(where={"userId": profile_data.userId})
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists for this user")
    date_of_birth_datetime = datetime.combine(profile_data.dateOfBirth, datetime.min.time())
    # ✅ Create the profile
    profile = await db.profile.create(
        data={
            "userId": profile_data.userId,
            "gender": profile_data.gender,
            "height": profile_data.height,
            "weight": profile_data.weight,
            "dateOfBirth": date_of_birth_datetime.isoformat() + "Z",
        }
    )

    return {"message": "Profile created successfully", "profile": profile}
