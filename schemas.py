from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Event Schemas
class EventCreate(BaseModel):
    name: str

class EventResponse(BaseModel):
    id: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

# Participant Schemas
class ParticipantCreate(BaseModel):
    name: str
    email: EmailStr

class ParticipantResponse(BaseModel):
    id: str
    event_id: str
    name: str
    email: str
    qr_token: str
    checked_in: bool
    check_in_time: Optional[datetime] = None
    created_at: datetime
    
    qr_image_url: Optional[str] = None

    class Config:
        from_attributes = True

# Check-in Schemas
class CheckInRequest(BaseModel):
    qr_token: str

class CheckInResponse(BaseModel):
    success: bool
    message: str
    participant: Optional[ParticipantResponse] = None

# Analytics Schema
class AnalyticsResponse(BaseModel):
    event_id: str
    event_name: str
    total_registered: int
    total_checked_in: int
    attendance_percentage: float
    participants: List[ParticipantResponse]
