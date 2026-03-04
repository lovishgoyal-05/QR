from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import models, schemas
from utils.qr_generator import generate_qr_code

def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Event).order_by(models.Event.created_at.desc()).offset(skip).limit(limit).all()

def get_event(db: Session, event_id: str):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(name=event.name)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def register_participant(db: Session, event_id: str, participant: schemas.ParticipantCreate):
    # Check if participant already exists in the event
    db_participant = db.query(models.Participant).filter(
        models.Participant.event_id == event_id,
        models.Participant.email == participant.email
    ).first()
    
    if db_participant:
        return None # Return None to let router throw 400

    db_participant = models.Participant(
        event_id=event_id,
        name=participant.name,
        email=participant.email
    )
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    
    # Generate physical QR file using the token
    qr_image_url = generate_qr_code(db_participant.qr_token, db_participant.qr_token)
    
    # We dynamically inject this into the response object
    setattr(db_participant, "qr_image_url", qr_image_url)
    
    return db_participant

def process_checkin(db: Session, qr_token: str):
    participant = db.query(models.Participant).filter(models.Participant.qr_token == qr_token).first()
    
    if not participant:
        return {"success": False, "message": "Invalid QR Token.", "status_code": 404}
        
    if participant.checked_in:
        return {"success": False, "message": "Duplicate Check-In! Participant already checked in.", "status_code": 409, "participant": participant}
        
    participant.checked_in = True
    participant.check_in_time = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(participant)
    
    return {"success": True, "message": "Check-in successful.", "status_code": 200, "participant": participant}

def get_event_analytics(db: Session, event_id: str):
    event = get_event(db, event_id)
    if not event:
        return None
        
    participants = db.query(models.Participant).filter(models.Participant.event_id == event_id).order_by(models.Participant.created_at.desc()).all()
    
    total_reg = len(participants)
    total_checkin = sum(1 for p in participants if p.checked_in)
    attendance_pct = (total_checkin / total_reg * 100) if total_reg > 0 else 0.0
    
    return schemas.AnalyticsResponse(
        event_id=event.id,
        event_name=event.name,
        total_registered=total_reg,
        total_checked_in=total_checkin,
        attendance_percentage=round(attendance_pct, 2),
        participants=participants
    )
