from fastapi import FastAPI, Depends, HTTPException, Response, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io

import models, schemas, crud
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QR Check-In System",
    description="Full-stack QR Check-In system using FastAPI, SQLAlchemy, and Jinja2.",
    version="1.0.0"
)

# Mount static files for CSS and QR images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")


# ==========================================
# FRONTEND UI Routes (HTML)
# ==========================================

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    events = crud.get_events(db)
    return templates.TemplateResponse("index.html", {"request": request, "events": events})


@app.get("/admin")
def admin_dashboard(request: Request, event_id: Optional[str] = None, db: Session = Depends(get_db)):
    events = crud.get_events(db)
    analytics = None
    selected_event = None

    if event_id:
        analytics = crud.get_event_analytics(db, event_id=event_id)
        selected_event = crud.get_event(db, event_id=event_id)

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "events": events,
        "analytics": analytics,
        "selected_event": selected_event
    })


@app.post("/admin/events")
def create_event_form(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    event_schema = schemas.EventCreate(name=name)
    crud.create_event(db=db, event=event_schema)
    
    # Refresh dashboard after creation
    events = crud.get_events(db)
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "events": events,
        "analytics": None,
        "selected_event": None
    })


@app.get("/events/{event_id}/register")
def register_page(request: Request, event_id: str, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id=event_id)
    if not event:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Event not found", "events": crud.get_events(db)})
        
    return templates.TemplateResponse("register.html", {"request": request, "event": event})


@app.post("/events/{event_id}/register")
def register_submit(
    request: Request, 
    event_id: str, 
    name: str = Form(...), 
    email: str = Form(...), 
    db: Session = Depends(get_db)
):
    event = crud.get_event(db, event_id=event_id)
    if not event:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Event not found", "events": crud.get_events(db)})
        
    participant_data = schemas.ParticipantCreate(name=name, email=email)
    db_participant = crud.register_participant(db, event_id=event_id, participant=participant_data)
    
    if db_participant is None:
        return templates.TemplateResponse("register.html", {"request": request, "event": event, "error": "Email already registered for this event."})
        
    return templates.TemplateResponse("success.html", {"request": request, "event": event, "participant": db_participant})


@app.get("/scanner")
def scanner_page(request: Request):
    return templates.TemplateResponse("scanner.html", {"request": request})


# ==========================================
# BACKEND API Routes (JSON)
# ==========================================

@app.post("/events/", response_model=schemas.EventResponse)
def api_create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event)


@app.get("/events/", response_model=List[schemas.EventResponse])
def api_list_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@app.post("/checkin/", response_model=schemas.CheckInResponse)
def api_process_checkin(request: schemas.CheckInRequest, db: Session = Depends(get_db)):
    result = crud.process_checkin(db, qr_token=request.qr_token)
    return result


@app.get("/admin/analytics/{event_id}", response_model=schemas.AnalyticsResponse)
def api_get_analytics(event_id: str, db: Session = Depends(get_db)):
    analytics = crud.get_event_analytics(db, event_id=event_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Event not found")
    return analytics


@app.get("/admin/export/{event_id}")
def export_csv(event_id: str, db: Session = Depends(get_db)):
    analytics = crud.get_event_analytics(db, event_id=event_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["ID", "Name", "Email", "Checked In", "Check-in Time", "Registration Time"])
    
    # Write rows
    for p in analytics.participants:
        check_in_time_str = p.check_in_time.isoformat() if p.check_in_time else "N/A"
        writer.writerow([p.id, p.name, p.email, "Yes" if p.checked_in else "No", check_in_time_str, p.created_at.isoformat()])
        
    csv_str = output.getvalue()
    
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=event_{event_id}_attendance.csv"}
    )
