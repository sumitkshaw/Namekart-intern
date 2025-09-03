from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uvicorn

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model - Updated with version field
class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models - Updated with version support
class NoteCreate(BaseModel):
    content: str

class NoteUpdate(BaseModel):
    content: str

class NoteUpdateWithVersion(BaseModel):
    content: str
    version: int

class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime
    version: int
    
    class Config:
        from_attributes = True

# FastAPI App
app = FastAPI(
    title="Notes API", 
    version="1.0.0",
    description="A simple CRUD Notes API with optimistic locking"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
        "https://your-app-name.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Routes
@app.get("/")
async def root():
    return {"message": "Notes API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/notes", response_model=List[NoteResponse])
async def get_notes(db: Session = Depends(get_db)):
    """Get all notes, ordered by creation date (newest first)"""
    notes = db.query(Note).order_by(Note.created_at.desc()).all()
    return notes

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get a specific note by ID"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.post("/api/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """Create a new note"""
    if not note.content.strip():
        raise HTTPException(status_code=400, detail="Note content cannot be empty")
    
    db_note = Note(content=note.content.strip(), version=1)  # ← Make sure this is explicit
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# Updated PUT endpoint with version control
@app.put("/api/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note_update: NoteUpdateWithVersion, db: Session = Depends(get_db)):
    """Update an existing note with optimistic locking"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if not note_update.content.strip():
        raise HTTPException(status_code=400, detail="Note content cannot be empty")
    
    # Optimistic locking check
    if note.version != note_update.version:
        raise HTTPException(
            status_code=409, 
            detail="Note was modified by another user. Please refresh and try again."
        )
    
    # Update with version increment
    note.content = note_update.content.strip()
    note.version += 1
    note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return note

# Legacy update endpoint (for backward compatibility)
@app.put("/api/notes/{note_id}/simple", response_model=NoteResponse)
async def update_note_simple(note_id: int, note_update: NoteUpdate, db: Session = Depends(get_db)):
    """Update an existing note (without version control)"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if not note_update.content.strip():
        raise HTTPException(status_code=400, detail="Note content cannot be empty")
    
    note.content = note_update.content.strip()
    note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)