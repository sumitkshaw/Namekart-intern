# setup_rag.py
"""
Setup script to initialize RAG pipeline and test it
"""
import sys
import subprocess
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing RAG dependencies...")
    
    packages = [
        "sentence-transformers==2.2.2",
        "scikit-learn==1.3.2",
        "numpy==1.24.3",
        "torch==2.1.0",
        "transformers==4.35.2"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def download_model():
    """Download and cache the sentence transformer model"""
    print("🤖 Downloading sentence transformer model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model downloaded and cached successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        return False

def test_rag_pipeline():
    """Test RAG pipeline with sample data"""
    print("🧪 Testing RAG pipeline...")
    
    try:
        from rag_service import SimpleRAG
        
        # Initialize RAG
        rag = SimpleRAG()
        
        # Test search
        result = rag.search_notes("test query")
        
        if result['success']:
            print("✅ RAG pipeline test successful!")
            print(f"📊 Indexed chunks: {len(rag.vector_store['documents'])}")
            return True
        else:
            print(f"❌ RAG test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ RAG pipeline error: {e}")
        return False

def create_sample_notes():
    """Create sample notes for testing"""
    print("📝 Creating sample notes for RAG testing...")
    
    try:
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect('./notes.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 1
            )
        ''')
        
        # Sample notes for RAG testing
        sample_notes = [
            "Meeting with team about project planning and timeline discussion",
            "Ideas for improving user experience in our mobile application",
            "Notes from conference about artificial intelligence and machine learning",
            "Grocery list: milk, bread, eggs, apples, bananas, chicken",
            "Book recommendations: Clean Code, Design Patterns, System Design",
            "Travel plans for summer vacation to Europe and Asia",
            "Daily workout routine: running, push-ups, squats, meditation",
            "Recipe for chocolate cake with vanilla frosting and berries"
        ]
        
        # Insert sample notes
        for note_content in sample_notes:
            cursor.execute('''
                INSERT INTO notes (content, created_at, updated_at, version)
                VALUES (?, ?, ?, ?)
            ''', (note_content, datetime.now(), datetime.now(), 1))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Created {len(sample_notes)} sample notes")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample notes: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up RAG Pipeline for Notes App")
    print("=" * 50)
    
    steps = [
        ("Installing Requirements", install_requirements),
        ("Downloading AI Model", download_model),
        ("Creating Sample Notes", create_sample_notes),
        ("Testing RAG Pipeline", test_rag_pipeline)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        success = step_func()
        
        if not success:
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please check the error messages above and try again.")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 RAG Pipeline Setup Complete!")
    print("\nNext steps:")
    print("1. Start your FastAPI server: python main.py")
    print("2. Test RAG endpoints:")
    print("   - GET  /api/rag/status")
    print("   - POST /api/notes/search")
    print("   - POST /api/rag/refresh")
    print("\n✨ Your Notes App now has AI-powered search!")
    
    return True

if __name__ == "__main__":
    main()