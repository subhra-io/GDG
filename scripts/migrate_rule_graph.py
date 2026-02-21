"""Migration script for rule graph features."""

import psycopg2
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings

def migrate():
    """Run rule graph migration."""
    print("🔄 Starting rule graph migration...")
    
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password or ""
        )
        
        cursor = conn.cursor()
        
        print("📝 Adding parent_rule_id column to compliance_rules...")
        cursor.execute("""
            ALTER TABLE compliance_rules 
            ADD COLUMN IF NOT EXISTS parent_rule_id UUID REFERENCES compliance_rules(id);
        """)
        
        print("📝 Adding precedence column to compliance_rules...")
        cursor.execute("""
            ALTER TABLE compliance_rules 
            ADD COLUMN IF NOT EXISTS precedence INTEGER DEFAULT 0;
        """)
        
        print("📝 Creating rule_dependencies table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rule_dependencies (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                rule_id UUID REFERENCES compliance_rules(id) ON DELETE CASCADE,
                depends_on_rule_id UUID REFERENCES compliance_rules(id) ON DELETE CASCADE,
                dependency_type VARCHAR(50) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(rule_id, depends_on_rule_id)
            );
        """)
        
        print("📝 Creating indexes for rule_dependencies...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rule_dependencies_rule_id 
            ON rule_dependencies(rule_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rule_dependencies_depends_on 
            ON rule_dependencies(depends_on_rule_id);
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Rule graph migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
