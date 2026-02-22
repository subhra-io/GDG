"""Migration script to create users table and update violations table."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from src.core.database import db_manager, Base
from src.models.user import User, UserRole
from src.models.violation import Violation

def migrate():
    """Create users table and update violations table."""
    print("🔄 Starting review workflow migration...")
    
    try:
        # Initialize database
        db_manager.initialize_postgres()
        engine = db_manager._postgres_engine
        
        # Create users table
        print("Creating users table...")
        Base.metadata.create_all(bind=engine, tables=[User.__table__])
        print("✅ Users table created")
        
        # Add columns to violations table
        print("Updating violations table...")
        with engine.connect() as conn:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'violations' 
                AND column_name IN ('assigned_to', 'is_false_positive')
            """))
            existing_columns = [row[0] for row in result]
            
            # Add assigned_to column if not exists
            if 'assigned_to' not in existing_columns:
                conn.execute(text("""
                    ALTER TABLE violations 
                    ADD COLUMN assigned_to UUID REFERENCES users(id)
                """))
                conn.commit()
                print("✅ Added assigned_to column")
            else:
                print("ℹ️  assigned_to column already exists")
            
            # Add is_false_positive column if not exists
            if 'is_false_positive' not in existing_columns:
                conn.execute(text("""
                    ALTER TABLE violations 
                    ADD COLUMN is_false_positive VARCHAR(10) DEFAULT 'false'
                """))
                conn.commit()
                print("✅ Added is_false_positive column")
            else:
                print("ℹ️  is_false_positive column already exists")
        
        # Create sample users
        print("\nCreating sample users...")
        from sqlalchemy.orm import Session
        session = Session(bind=engine)
        
        try:
            # Check if users exist
            user_count = session.query(User).count()
            
            if user_count == 0:
                users = [
                    User(email='admin@policysentinel.com', name='Admin User', role=UserRole.ADMIN),
                    User(email='john.doe@policysentinel.com', name='John Doe', role=UserRole.REVIEWER),
                    User(email='jane.smith@policysentinel.com', name='Jane Smith', role=UserRole.REVIEWER),
                    User(email='viewer@policysentinel.com', name='Viewer User', role=UserRole.VIEWER)
                ]
                session.add_all(users)
                session.commit()
                print("✅ Created 4 sample users")
            else:
                print(f"ℹ️  {user_count} users already exist")
        finally:
            session.close()
        
        print("\n📊 Migration Summary:")
        print("  - users table: ✅ Created")
        print("  - violations.assigned_to: ✅ Added")
        print("  - violations.is_false_positive: ✅ Added")
        print("  - sample users: ✅ Created")
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
