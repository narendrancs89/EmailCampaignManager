import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text

def migrate_add_optimal_send_time():
    """
    Add optimal send time fields to the scheduled_job table
    """
    try:
        # Connect to the database
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("DATABASE_URL environment variable not found.")
            return False
        
        # Create SQLAlchemy engine
        engine = create_engine(database_url)
        
        # Define the new columns to add
        new_columns = [
            ("use_optimal_time", "BOOLEAN DEFAULT FALSE"),
            ("optimal_time_window_start", "INTEGER DEFAULT 9"), 
            ("optimal_time_window_end", "INTEGER DEFAULT 17"),
            ("optimal_day_preference", "VARCHAR(50) DEFAULT 'weekday'")
        ]
        
        # Add each column if it doesn't exist
        with engine.connect() as connection:
            for column_name, column_definition in new_columns:
                # Check if column exists
                check_sql = text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'scheduled_job' AND column_name = :column_name
                """)
                
                result = connection.execute(check_sql, {"column_name": column_name})
                column_exists = result.fetchone()
                
                if not column_exists:
                    print(f"Adding column '{column_name}' to scheduled_job table...")
                    alter_sql = text(f"ALTER TABLE scheduled_job ADD COLUMN {column_name} {column_definition}")
                    connection.execute(alter_sql)
                    connection.commit()
                    print(f"Added column '{column_name}' successfully")
                else:
                    print(f"Column '{column_name}' already exists, skipping")
        
        print("Migration completed successfully!")
        return True
    
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting migration to add optimal send time fields...")
    if migrate_add_optimal_send_time():
        print("Migration completed successfully!")
    else:
        print("Migration failed.")
        sys.exit(1)