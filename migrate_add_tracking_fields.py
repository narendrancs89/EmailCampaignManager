from app import app, db
from sqlalchemy import text

def migrate_tracking_fields():
    """Add tracking fields to the email_template table"""
    with app.app_context():
        # Use the newer API with with statement
        connection = db.engine.connect()
        
        try:
            # Check if columns already exist
            check_columns_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'email_template' AND column_name IN "
                "('has_click_tracking', 'has_open_tracking', 'has_optout', 'click_tracking_url', 'open_tracking_url', 'optout_url', 'tracking_image_url')"
            )
            result = connection.execute(check_columns_query)
            existing_columns = [row[0] for row in result]
            
            print("Existing tracking columns:", existing_columns)
            
            # Add has_click_tracking if it doesn't exist
            if 'has_click_tracking' not in existing_columns:
                print("Adding has_click_tracking column...")
                connection.execute(text("ALTER TABLE email_template ADD COLUMN has_click_tracking BOOLEAN DEFAULT FALSE"))
            
            # Add has_open_tracking if it doesn't exist
            if 'has_open_tracking' not in existing_columns:
                print("Adding has_open_tracking column...")
                connection.execute(text("ALTER TABLE email_template ADD COLUMN has_open_tracking BOOLEAN DEFAULT FALSE"))
            
            # Add has_optout if it doesn't exist
            if 'has_optout' not in existing_columns:
                print("Adding has_optout column...")
                connection.execute(text("ALTER TABLE email_template ADD COLUMN has_optout BOOLEAN DEFAULT FALSE"))
            
            # Add click_tracking_url if it doesn't exist
            if 'click_tracking_url' not in existing_columns:
                print("Adding click_tracking_url column...")
                connection.execute(text("ALTER TABLE email_template ADD COLUMN click_tracking_url VARCHAR(500)"))
            
            # Add open_tracking_url if it doesn't exist
            if 'open_tracking_url' not in existing_columns:
                print("Adding open_tracking_url column...")
                connection.execute(text("ALTER TABLE email_template ADD COLUMN open_tracking_url VARCHAR(500)"))
            
            # Add optout_url if it doesn't exist
            if 'optout_url' not in existing_columns:
                print("Adding optout_url column...")
                connection.execute(text("ALTER TABLE email_template ADD COLUMN optout_url VARCHAR(500)"))
            
            # Add tracking_image_url if it doesn't exist
            if 'tracking_image_url' not in existing_columns:
                print("Adding tracking_image_url column...")
                connection.execute(text("ALTER TABLE email_template ADD COLUMN tracking_image_url VARCHAR(500)"))
                
            print("Database migration completed successfully!")
        finally:
            connection.close()

if __name__ == "__main__":
    migrate_tracking_fields()