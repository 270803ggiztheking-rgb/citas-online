"""
Sistema de Citas Online - Main Application
FastAPI backend for appointment booking
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time, timedelta
from typing import Optional
import sqlite3
import json
from pathlib import Path

app = FastAPI(
    title="Sistema de Citas Online",
    description="API para gestión de citas y reservaciones",
    version="1.0.0"
)

# Static files and templates
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Database setup
DB_PATH = BASE_DIR / "citas.db"


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Businesses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Services table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            duration_minutes INTEGER DEFAULT 30,
            price REAL,
            FOREIGN KEY (business_id) REFERENCES businesses(id)
        )
    """)
    
    # Available slots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS available_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            FOREIGN KEY (business_id) REFERENCES businesses(id)
        )
    """)
    
    # Appointments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            client_name TEXT NOT NULL,
            client_email TEXT NOT NULL,
            client_phone TEXT,
            appointment_date DATE NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    """)
    
    conn.commit()
    conn.close()


# Initialize DB on startup
init_db()


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class BusinessCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int = 30
    price: Optional[float] = None


class AppointmentCreate(BaseModel):
    service_id: int
    client_name: str
    client_email: EmailStr
    client_phone: Optional[str] = None
    appointment_date: date
    appointment_time: str
    notes: Optional[str] = None


class SlotCreate(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: str  # "09:00"
    end_time: str    # "18:00"


# ═══════════════════════════════════════════════════════════════════════════════
# FRONTEND ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/book/{business_slug}", response_class=HTMLResponse)
async def booking_page(request: Request, business_slug: str):
    """Booking page for a specific business."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM businesses WHERE slug = ?", (business_slug,))
    business = cursor.fetchone()
    conn.close()
    
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    
    return templates.TemplateResponse("booking.html", {
        "request": request,
        "business": dict(business)
    })


# ═══════════════════════════════════════════════════════════════════════════════
# API: BUSINESSES
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/businesses")
async def create_business(business: BusinessCreate):
    """Create a new business."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO businesses (name, slug, description, address, phone, email) VALUES (?, ?, ?, ?, ?, ?)",
            (business.name, business.slug, business.description, business.address, business.phone, business.email)
        )
        conn.commit()
        business_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El slug ya existe")
    finally:
        conn.close()
    
    return {"id": business_id, "message": "Negocio creado exitosamente"}


@app.get("/api/businesses/{business_id}")
async def get_business(business_id: int):
    """Get business details."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM businesses WHERE id = ?", (business_id,))
    business = cursor.fetchone()
    conn.close()
    
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    
    return dict(business)


# ═══════════════════════════════════════════════════════════════════════════════
# API: SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/businesses/{business_id}/services")
async def create_service(business_id: int, service: ServiceCreate):
    """Add a service to a business."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO services (business_id, name, description, duration_minutes, price) VALUES (?, ?, ?, ?, ?)",
        (business_id, service.name, service.description, service.duration_minutes, service.price)
    )
    conn.commit()
    service_id = cursor.lastrowid
    conn.close()
    
    return {"id": service_id, "message": "Servicio agregado"}


@app.get("/api/businesses/{business_id}/services")
async def get_services(business_id: int):
    """Get all services for a business."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE business_id = ?", (business_id,))
    services = cursor.fetchall()
    conn.close()
    
    return [dict(s) for s in services]


# ═══════════════════════════════════════════════════════════════════════════════
# API: AVAILABLE SLOTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/businesses/{business_id}/slots")
async def create_slot(business_id: int, slot: SlotCreate):
    """Add available time slot for a business."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO available_slots (business_id, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?)",
        (business_id, slot.day_of_week, slot.start_time, slot.end_time)
    )
    conn.commit()
    conn.close()
    
    return {"message": "Horario agregado"}


@app.get("/api/businesses/{business_id}/available-times")
async def get_available_times(business_id: int, date_str: str, service_id: int):
    """Get available appointment times for a specific date."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Parse date
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    day_of_week = target_date.weekday()
    
    # Get business hours for this day
    cursor.execute(
        "SELECT start_time, end_time FROM available_slots WHERE business_id = ? AND day_of_week = ?",
        (business_id, day_of_week)
    )
    slots = cursor.fetchall()
    
    if not slots:
        return {"available_times": [], "message": "No hay horario disponible para este día"}
    
    # Get service duration
    cursor.execute("SELECT duration_minutes FROM services WHERE id = ?", (service_id,))
    service = cursor.fetchone()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    duration = service["duration_minutes"]
    
    # Get existing appointments for this date
    cursor.execute(
        "SELECT appointment_time FROM appointments WHERE business_id = ? AND appointment_date = ? AND status != 'cancelled'",
        (business_id, date_str)
    )
    booked_times = [row["appointment_time"] for row in cursor.fetchall()]
    conn.close()
    
    # Generate available time slots
    available_times = []
    for slot in slots:
        start = datetime.strptime(slot["start_time"], "%H:%M")
        end = datetime.strptime(slot["end_time"], "%H:%M")
        
        current = start
        while current + timedelta(minutes=duration) <= end:
            time_str = current.strftime("%H:%M")
            if time_str not in booked_times:
                available_times.append(time_str)
            current += timedelta(minutes=30)  # 30-min intervals
    
    return {"available_times": available_times, "date": date_str}


# ═══════════════════════════════════════════════════════════════════════════════
# API: APPOINTMENTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/businesses/{business_id}/appointments")
async def create_appointment(business_id: int, appointment: AppointmentCreate):
    """Book an appointment."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify the time is available
    cursor.execute(
        "SELECT id FROM appointments WHERE business_id = ? AND appointment_date = ? AND appointment_time = ? AND status != 'cancelled'",
        (business_id, str(appointment.appointment_date), appointment.appointment_time)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Este horario ya está reservado")
    
    # Create appointment
    cursor.execute(
        """INSERT INTO appointments 
           (business_id, service_id, client_name, client_email, client_phone, appointment_date, appointment_time, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (business_id, appointment.service_id, appointment.client_name, appointment.client_email,
         appointment.client_phone, str(appointment.appointment_date), appointment.appointment_time, appointment.notes)
    )
    conn.commit()
    appointment_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": appointment_id,
        "message": "¡Cita reservada exitosamente!",
        "details": {
            "fecha": str(appointment.appointment_date),
            "hora": appointment.appointment_time,
            "cliente": appointment.client_name
        }
    }


@app.get("/api/businesses/{business_id}/appointments")
async def get_appointments(business_id: int, date_from: Optional[str] = None, date_to: Optional[str] = None):
    """Get appointments for a business."""
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT a.*, s.name as service_name 
        FROM appointments a 
        JOIN services s ON a.service_id = s.id 
        WHERE a.business_id = ?
    """
    params = [business_id]
    
    if date_from:
        query += " AND a.appointment_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND a.appointment_date <= ?"
        params.append(date_to)
    
    query += " ORDER BY a.appointment_date, a.appointment_time"
    
    cursor.execute(query, params)
    appointments = cursor.fetchall()
    conn.close()
    
    return [dict(a) for a in appointments]


@app.patch("/api/appointments/{appointment_id}/status")
async def update_appointment_status(appointment_id: int, status: str):
    """Update appointment status (confirmed, cancelled, completed)."""
    valid_statuses = ["pending", "confirmed", "cancelled", "completed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Use: {valid_statuses}")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()
    
    return {"message": f"Cita actualizada a: {status}"}


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO DATA
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/setup-demo")
async def setup_demo():
    """Create demo business with services and schedule."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if demo already exists
    cursor.execute("SELECT id FROM businesses WHERE slug = 'demo-consultorio'")
    if cursor.fetchone():
        return {"message": "Demo ya existe", "url": "/book/demo-consultorio"}
    
    # Create demo business
    cursor.execute(
        """INSERT INTO businesses (name, slug, description, address, phone, email)
           VALUES (?, ?, ?, ?, ?, ?)""",
        ("Consultorio Dental Sonrisas", "demo-consultorio",
         "Tu sonrisa es nuestra prioridad. Servicios dentales de calidad.",
         "Calle 60 #123, Centro, Mérida, Yucatán",
         "+52 999 123 4567", "citas@sonrisas.com")
    )
    business_id = cursor.lastrowid
    
    # Add services
    services = [
        ("Limpieza Dental", "Limpieza profunda con ultrasonido", 45, 500),
        ("Consulta General", "Revisión y diagnóstico", 30, 300),
        ("Blanqueamiento", "Blanqueamiento dental profesional", 60, 2500),
        ("Extracción Simple", "Extracción de piezas dentales", 30, 800),
    ]
    for name, desc, duration, price in services:
        cursor.execute(
            "INSERT INTO services (business_id, name, description, duration_minutes, price) VALUES (?, ?, ?, ?, ?)",
            (business_id, name, desc, duration, price)
        )
    
    # Add schedule (Mon-Fri 9:00-18:00, Sat 9:00-14:00)
    for day in range(5):  # Monday to Friday
        cursor.execute(
            "INSERT INTO available_slots (business_id, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?)",
            (business_id, day, "09:00", "18:00")
        )
    cursor.execute(
        "INSERT INTO available_slots (business_id, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?)",
        (business_id, 5, "09:00", "14:00")  # Saturday
    )
    
    conn.commit()
    conn.close()
    
    return {
        "message": "Demo creado exitosamente",
        "business_id": business_id,
        "url": "/book/demo-consultorio"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
