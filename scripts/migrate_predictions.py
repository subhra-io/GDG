"""Migration script to create predictions table."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from src.core.database import db_manager
from src.models.prediction import Prediction
from src.core.database import Base

def migrate():
    """Create predictions table."""
    print("🔄 Starting predictions table migration...")
    
    try:
        # Initialize database
        db_manager.initialize_postgres()
        engine = db_manager._postgres_engine
        
        # Create predictions table
        print("Creating predictions table...")
        Base.metadata.create_all(bind=engine, tables=[Prediction.__table__])
        
        print("✅ Predictions table created successfully!")
        
        # Verify table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'predictions'
            """))
            
            if result.fetchone():
                print("✅ Verified: predictions table exists")
            else:
                print("❌ Error: predictions table not found")
                return False
        
        print("\n📊 Migration Summary:")
        print("  - predictions table: ✅ Created")
        print("\n✅ Migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db_manager.close_all()


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
