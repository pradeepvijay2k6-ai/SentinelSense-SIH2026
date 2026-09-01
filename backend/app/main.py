from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base, SessionLocal
from .models import Personnel
from .api import personnel, upload, analysis, samples, roster

# Create tables
Base.metadata.create_all(bind=engine)

def seed_initial_demo_data():
    db = SessionLocal()
    try:
        if db.query(Personnel).count() == 0:
            demo_officers = [
                {"id": "CRPF-0101", "name": "Inspector Rajesh Kumar", "force": "CRPF", "unit": "114 Bn, Srinagar Sector", "age": 34},
                {"id": "CRPF-0234", "name": "Sub-Inspector Amit Verma", "force": "CRPF", "unit": "205 CoBRA, Gaya", "age": 29},
                {"id": "BSF-0512", "name": "Head Constable Vikram Singh", "force": "BSF", "unit": "48 Bn, Samba Sector", "age": 38},
                {"id": "ITBP-0891", "name": "Constable Tsering Dorje", "force": "ITBP", "unit": "24 Bn, Ladakh Border", "age": 31},
                {"id": "CISF-0320", "name": "Assistant Sub-Inspector Priya Nair", "force": "CISF", "unit": "ASG Delhi Airport", "age": 35},
            ]
            for o in demo_officers:
                p = Personnel(
                    personnel_id=o["id"],
                    name=o["name"],
                    force_type=o["force"],
                    unit=o["unit"],
                    age=o["age"]
                )
                db.add(p)
            db.commit()
            print("Seeded demo CAPF personnel profiles.")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_demo_data()
    yield

app = FastAPI(
    title="SentinelSense API",
    description="Multimodal Biosignal Processing & Predictive Stress/Fatigue AI for CAPF Personnel (SIH 2026 Problem Statement 26186)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(personnel.router)
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(samples.router)
app.include_router(roster.router)

@app.get("/")
def health_check():
    return {
        "system": "SentinelSense",
        "status": "operational",
        "version": "1.0.0",
        "problem_statement": "SIH 2026 PS 26186 (CAPF Stress & Sleep Monitoring)",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
