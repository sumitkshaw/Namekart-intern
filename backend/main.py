from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uvicorn
import os

# RAG IMPORT COMMENTED OUT
# from rag_service import SimpleRAG
from pydantic import BaseModel

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# RAG SERVICE COMMENTED OUT
# rag_service = SimpleRAG()

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
        
class RAGQuery(BaseModel):
    query: str
    top_k: int = 3

class RAGResponse(BaseModel):
    success: bool
    response: str
    sources: List[dict]
    context_used: List[str]
    query: str
    timestamp: str

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
        "http://localhost:3000",           # Local development
        "http://127.0.0.1:3000",          # Local development  
        "https://*.vercel.app",           # Vercel deployments
        "https://*.netlify.app",          # Netlify deployments
        "https://*.railway.app",          # Railway frontend deployments
        "*"                               # Allow all for assignment (temporary)
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
    
    # RAG FUNCTIONALITY COMMENTED OUT
    # try:
    #     rag_service.add_note_to_vector_store(
    #         note_id=db_note.id,
    #         content=db_note.content,
    #         created_at=db_note.created_at.isoformat(),
    #         updated_at=db_note.updated_at.isoformat(),
    #         version=db_note.version
    #     )
    # except Exception as e:
    #     print(f"Warning: Failed to add note to RAG index: {e}")
    
    return db_note

@app.post("/api/notes/search", response_model=dict)
async def search_notes_rag(query_data: RAGQuery, db: Session = Depends(get_db)):
    """RAG-powered note search - TEMPORARILY DISABLED"""
    # RAG FUNCTIONALITY COMMENTED OUT - RETURNING PLACEHOLDER
    return {
        "success": True,
        "response": "RAG search is temporarily disabled during deployment",
        "sources": [],
        "context_used": [],
        "query": query_data.query,
        "timestamp": datetime.utcnow().isoformat()
    }
    # try:
    #     # Ensure vector store is up to date
    #     rag_service.load_notes_to_vector_store()
    #     
    #     # Perform RAG search
    #     result = rag_service.search_notes(query_data.query, query_data.top_k)
    #     
    #     return result
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"RAG search failed: {str(e)}")

@app.post("/api/rag/refresh")
async def refresh_rag_index(db: Session = Depends(get_db)):
    """Refresh RAG vector store with latest notes - TEMPORARILY DISABLED"""
    # RAG FUNCTIONALITY COMMENTED OUT - RETURNING SUCCESS MESSAGE
    return {"message": "RAG refresh endpoint is temporarily disabled"}
    # try:
    #     rag_service.load_notes_to_vector_store()
    #     return {"message": "RAG index refreshed successfully"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"RAG refresh failed: {str(e)}")

@app.get("/api/rag/status")
async def rag_status():
    """Get RAG system status - TEMPORARILY DISABLED"""
    # RAG FUNCTIONALITY COMMENTED OUT - RETURNING DISABLED STATUS
    return {
        "status": "disabled",
        "message": "RAG functionality is temporarily disabled for deployment",
        "indexed_chunks": 0,
        "model": "none",
        "vector_dimensions": 0
    }
    # try:
    #     doc_count = len(rag_service.vector_store['documents'])
    #     return {
    #         "status": "active",
    #         "indexed_chunks": doc_count,
    #         "model": "sentence-transformers/all-MiniLM-L6-v2",
    #         "vector_dimensions": 384
    #     }
    # except Exception as e:
    #     return {
    #         "status": "error",
    #         "error": str(e)
    #     }

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
    
    # RAG REFRESH COMMENTED OUT
    # try:
    #     rag_service.load_notes_to_vector_store()
    # except Exception as e:
    #     print(f"Warning: Failed to refresh RAG index: {e}")
    
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)