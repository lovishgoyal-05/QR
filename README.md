# FastAPI QR Check-In System

A robust, backend-focused QR Check-In system built with FastAPI and SQLAlchemy designed to manage event attendance.
This system enables organizers to create events, uniquely register participants, issue scannable QR codes, and reliably verify attendance while preventing duplicate check-ins.

## Features

- **UUID4 Security**: Tokens and primary keys use UUID4 for cryptographic randomness, preventing ID guessing.
- **Relational Integrity**: Built on SQLAlchemy using SQLite, strictly scoping participants to specific events.
- **Dynamic QR Generation**: Employs `qrcode` to generate physical `.png` assets dynamically stored on the server.
- **Analytics & Export**: Provides attendance metrics (checked-in vs registered) and allows exporting complete participant logs as CSV.
- **FastAPI Perks**: Leverages Pydantic validation and automatic Swagger UI generation.

## UI Application Architecture

```
fastapi-qr-checkin/
├── main.py                 # FastAPI application and route definitions (HTML & JSON)
├── database.py             # SQLAlchemy engine & session config
├── models.py               # ORM Database Schema
├── schemas.py              # Pydantic validation schemas
├── crud.py                 # DB Data access abstractions
├── utils/qr_generator.py   # PNG QR logic
├── templates/              # Jinja2 HTML Views
│   ├── base.html
│   ├── index.html          # Public Event Portal
│   ├── admin.html          # Admin Dashboard
│   ├── register.html       # Signup Form
│   ├── success.html        # QR Delivery Screen
│   └── scanner.html        # html5-qrcode Webcam verification
├── static/
│   ├── styles.css          # Premium Vanilla CSS styles
│   └── *.png               # Generated QR codes
├── requirements.txt
└── Dockerfile
```

## Setup Instructions

### Local Development
1. Navigate into the application folder:
   ```bash
   cd fastapi-qr-checkin
   ```
2. Create and activate a Virtual Environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server (uvicorn):
   ```bash
   uvicorn main:app --reload
   ```

## Usage Flow (GUI)

Once the application is running at `http://127.0.0.1:8000/`, you can use the interactive Graphical Interface:

1. **Admin Portal**: Navigate to `/admin`. Use the form to instantly create events. Selecting an event loads your real-time participant ledger and attendance percentages.
2. **Public Registration**: Users landing on the root `/` page are presented with valid events. Upon selecting an event, they fill out an HTML form and get their QR code rendered securely in the browser. 
3. **Scanner Kiosk**: Staff visit `/scanner` to activate their device's webcam. The JavaScript securely pings the FastAPI backend `/checkin/` route and visually confirms or denies attendance dynamically without page reloads.

*Note: Programmatic interaction and testing is still supported JSON-to-JSON via the Swagger UI available at `/docs`.*

## Screenshots Placeholder
*(Add screenshots of your mobile scanner, Admin dashboard UI, or Swagger documentation here for visual reference).*

## Future Improvements
- **Role-Based Access Control (RBAC)**: Secure admin endpoints using JWT validation so only event organizers can create events or view analytics.
- **Scanner App Auth**: Introduce an API key mechanism on the `/checkin/` route to authenticate IoT scanning hardware or staff devices.
- **Expirable QR Codes**: Generate rotating JWT-backed QR encodings (e.g., OTP) instead of static UUIDs for highly secure venues.
- **Rate Limiting**: Apply request throttles on the check-in route to deter brute force attacks if scanners are placed publicly.
- **Cloud Object Storage (S3)**: Migrate QR code file generation to S3 instead of local `static/` storage for better stateless horizontal scaling.
