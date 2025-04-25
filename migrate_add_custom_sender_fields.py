import sys
import sqlite3
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.declarative import declarative_base
from app import db

def migrate_custom_sender_fields():
    """Add custom sender fields to the scheduled_job table"""
    print("Running migration to add custom sender fields to scheduled_job table...")
    
    # Check if columns already exist
    inspector = Inspector.from_engine(db.engine)
    columns = [c['name'] for c in inspector.get_columns('scheduled_job')]
    
    # Only add columns if they don't already exist
    if 'from_email' not in columns:
        print("Adding 'from_email' column to scheduled_job table...")
        with db.engine.connect() as connection:
            connection.execute(sa.text(
                "ALTER TABLE scheduled_job ADD COLUMN from_email VARCHAR(120)"
            ))
    else:
        print("'from_email' column already exists.")
        
    if 'from_name' not in columns:
        print("Adding 'from_name' column to scheduled_job table...")
        with db.engine.connect() as connection:
            connection.execute(sa.text(
                "ALTER TABLE scheduled_job ADD COLUMN from_name VARCHAR(120)"
            ))
    else:
        print("'from_name' column already exists.")
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_custom_sender_fields()