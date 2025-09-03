from sqlalchemy import create_engine, text
import os

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def add_version_column():
    """Add version column to existing notes table"""
    with engine.connect() as connection:
        try:
            # Check if version column already exists
            result = connection.execute(text("PRAGMA table_info(notes)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'version' not in columns:
                # Add version column with default value 1
                connection.execute(text("ALTER TABLE notes ADD COLUMN version INTEGER DEFAULT 1"))
                connection.commit()
                print("✅ Version column added successfully")
            else:
                print("ℹ️ Version column already exists")
                
        except Exception as e:
            print(f"❌ Error adding version column: {e}")

if __name__ == "__main__":
    add_version_column()