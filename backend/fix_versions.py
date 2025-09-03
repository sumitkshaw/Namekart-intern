from sqlalchemy import create_engine, text
import os

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def fix_versions():
    """Fix version values for existing notes"""
    with engine.connect() as connection:
        try:
            # Update any NULL versions to 1
            result = connection.execute(text("""
                UPDATE notes 
                SET version = 1 
                WHERE version IS NULL OR version = 0
            """))
            connection.commit()
            
            # Check current state
            result = connection.execute(text("SELECT id, version FROM notes ORDER BY id"))
            notes = result.fetchall()
            
            print("Current note versions:")
            for note in notes:
                print(f"Note ID {note[0]}: version {note[1]}")
            
            print(f"✅ Fixed versions for {len(notes)} notes")
            
        except Exception as e:
            print(f"❌ Error fixing versions: {e}")

if __name__ == "__main__":
    fix_versions()