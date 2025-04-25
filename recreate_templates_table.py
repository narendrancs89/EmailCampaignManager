from app import app, db
from models import EmailTemplate
from sqlalchemy import text

def recreate_templates_table():
    """Drop and recreate the email_template table with all required fields"""
    with app.app_context():
        connection = db.engine.connect()
        
        try:
            # Back up existing templates
            print("Fetching existing templates...")
            backup_query = text("SELECT id, name, subject, content, type, user_id, created_at, updated_at FROM email_template")
            result = connection.execute(backup_query)
            templates = [dict(row._mapping) for row in result]
            print(f"Found {len(templates)} templates to back up.")
            
            # Drop the table
            print("Dropping email_template table...")
            connection.execute(text("DROP TABLE IF EXISTS email_template CASCADE"))
            connection.commit()
            
            # Create all tables (this will create a fresh email_template with all columns from the model)
            print("Creating tables from the model definitions...")
            db.create_all()
            
            # Restore backed up templates with default values for new columns
            if templates:
                print("Restoring templates with new schema...")
                for template in templates:
                    insert_query = text("""
                        INSERT INTO email_template 
                        (id, name, subject, content, type, user_id, created_at, updated_at, 
                         has_click_tracking, has_open_tracking, has_optout, 
                         click_tracking_url, open_tracking_url, optout_url, tracking_image_url)
                        VALUES 
                        (:id, :name, :subject, :content, :type, :user_id, :created_at, :updated_at,
                         FALSE, FALSE, FALSE, NULL, NULL, NULL, NULL)
                    """)
                    connection.execute(insert_query, template)
                connection.commit()
                print("Templates restored successfully.")
            
            print("Table recreation completed successfully!")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    recreate_templates_table()