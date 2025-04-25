import os
import sys
import psycopg2
from psycopg2 import sql

# Get the database URL from environment variable
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("DATABASE_URL environment variable is not set")
    sys.exit(1)

# Connect to the database
try:
    conn = psycopg2.connect(database_url)
    conn.autocommit = False
    cursor = conn.cursor()
    print("Connected to the database")
except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)

# Define columns to add to scheduled_job
job_columns = [
    ("started_at", "TIMESTAMP"),
    ("completed_at", "TIMESTAMP"),
    ("current_batch", "INTEGER DEFAULT 0"),
    ("batch_size", "INTEGER DEFAULT 100"),
    ("sending_started_at", "TIMESTAMP"),
    ("sending_completed_at", "TIMESTAMP"),
    ("avg_sending_rate", "FLOAT DEFAULT 0.0")
]

# Define columns to add to email_template
template_columns = [
    ("is_draft", "BOOLEAN DEFAULT FALSE"),
    ("parent_id", "INTEGER"),
    ("version", "INTEGER DEFAULT 1")
]

try:
    # Check if columns exist in scheduled_job
    for column_name, _ in job_columns:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'scheduled_job' AND column_name = %s",
            (column_name,)
        )
        if not cursor.fetchone():
            # Column doesn't exist, add it
            print(f"Adding column '{column_name}' to scheduled_job table")
            cursor.execute(
                sql.SQL("ALTER TABLE scheduled_job ADD COLUMN {} {}").format(
                    sql.Identifier(column_name),
                    sql.SQL(_)
                )
            )
        else:
            print(f"Column '{column_name}' already exists in scheduled_job table")

    # Check if columns exist in email_template
    for column_name, _ in template_columns:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'email_template' AND column_name = %s",
            (column_name,)
        )
        if not cursor.fetchone():
            # Column doesn't exist, add it
            print(f"Adding column '{column_name}' to email_template table")
            cursor.execute(
                sql.SQL("ALTER TABLE email_template ADD COLUMN {} {}").format(
                    sql.Identifier(column_name),
                    sql.SQL(_)
                )
            )
        else:
            print(f"Column '{column_name}' already exists in email_template table")
    
    # Check if foreign key constraint exists
    cursor.execute(
        "SELECT 1 FROM information_schema.table_constraints "
        "WHERE constraint_name = 'fk_parent_template' AND table_name = 'email_template'"
    )
    if not cursor.fetchone():
        # Add foreign key constraint for parent_id
        print("Adding foreign key constraint for parent_id")
        cursor.execute(
            "ALTER TABLE email_template "
            "ADD CONSTRAINT fk_parent_template FOREIGN KEY (parent_id) REFERENCES email_template(id)"
        )
    else:
        print("Foreign key constraint already exists")
    
    # Commit the transaction
    conn.commit()
    print("Migration completed successfully")
    
except Exception as e:
    conn.rollback()
    print(f"Error during migration: {e}")
    sys.exit(1)
    
finally:
    cursor.close()
    conn.close()
    print("Database connection closed")