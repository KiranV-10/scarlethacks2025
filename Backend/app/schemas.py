from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

# ---------------------
# User Schemas
# ---------------------

class UserCreate(BaseModel):
    name: Optional[str] = None
    email: str

class UserOut(BaseModel):
    id: str
    name: Optional[str] = None
    email: str
    emailVerified: Optional[datetime] = None
    image: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

# ---------------------
# Journal Entry Schemas
# ---------------------

class JournalEntryCreate(BaseModel):
    entryTitle: str
    entryDate: date
    medicationsTaken: Optional[str] = None
    symptomsHad: Optional[str] = None
    sleep: Optional[Decimal] = None
    otherNotes: Optional[str] = None
    userId: str

class JournalEntryOut(BaseModel):
    id: str
    entryTitle: str
    entryDate: date
    medicationsTaken: Optional[str] = None
    symptomsHad: Optional[str] = None
    sleep: Optional[Decimal] = None
    otherNotes: Optional[str] = None
    userId: str

# ---------------------
# Health Service Schemas
# ---------------------

class HealthServiceCreate(BaseModel):
    name: str
    type: str
    address: str
    latitude: float
    longitude: float

class HealthServiceOut(BaseModel):
    id: str
    name: str
    type: str
    address: str
    latitude: float
    longitude: float
    lastVerified: Optional[datetime] = None
    status: str
