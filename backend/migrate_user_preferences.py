"""
Quick migration script to add UserPreferences table
Run this to add the new table to your existing database
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.models import Base, UserPreferences
import sys

def run_migration():
    """Create UserPreferences table if it doesn't exist"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_preferences'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("UserPreferences table already exists!")
                return
        
        # Create the table
        print("Creating UserPreferences table...")
        Base.metadata.tables['user_preferences'].create(engine)
        print("UserPreferences table created successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()