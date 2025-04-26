"""
This migration script adds the actual_send_time field to the ScheduledJob model.
"""
import os
import sys
from datetime import datetime
import sqlalchemy as sa
from app import db, app

def run_migration():
    """Add actual_send_time field to the ScheduledJob table"""
    print("Starting migration: Adding actual_send_time field to ScheduledJob table")
    
    with app.app_context():
        # Check if the column already exists
        inspector = sa.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('scheduled_job')]
        
        if 'actual_send_time' not in columns:
            # Add the new columns
            print("Adding actual_send_time column to scheduled_job table")
            
            # Create the migration
            migration = """
            ALTER TABLE scheduled_job ADD COLUMN IF NOT EXISTS actual_send_time TIMESTAMP;
            """
            
            # Execute the migration
            try:
                db.session.execute(sa.text(migration))
                db.session.commit()
                print("Migration successful!")
            except Exception as e:
                db.session.rollback()
                print(f"Error during migration: {str(e)}")
                sys.exit(1)
        else:
            print("Migration already applied - actual_send_time column already exists")

if __name__ == "__main__":
    run_migration()