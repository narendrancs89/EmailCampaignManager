import os
import sys
import json
import datetime
import getpass
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, EmailSegment, Contact, EmailTemplate, SMTPConfig, ScheduledJob

def restore_data(backup_timestamp=None):
    """
    Restore data from JSON backup files
    If no timestamp is provided, use the most recent backup
    """
    # Find backup directory
    backup_dir = 'database_backups'
    if not os.path.exists(backup_dir):
        print(f"Error: Backup directory '{backup_dir}' not found.")
        return False
    
    # Find backup files with specified timestamp or most recent
    if backup_timestamp:
        timestamp = backup_timestamp
    else:
        # Find most recent backup by listing all user backup files and sorting by name
        user_backups = [f for f in os.listdir(backup_dir) if f.startswith('users_')]
        if not user_backups:
            print(f"Error: No backup files found in '{backup_dir}'.")
            return False
        
        # Sort by timestamp (part of filename)
        user_backups.sort(reverse=True)
        timestamp = user_backups[0].split('users_')[1].split('.json')[0]
    
    print(f"Restoring data from backup with timestamp: {timestamp}")
    
    # Define files to restore
    files_to_restore = [
        ('users', User),
        ('segments', EmailSegment),
        ('contacts', Contact),
        ('templates', EmailTemplate), 
        ('smtp_configs', SMTPConfig),
        ('jobs', ScheduledJob)
    ]
    
    try:
        with app.app_context():
            # For each model type
            for file_prefix, model_class in files_to_restore:
                file_path = f"{backup_dir}/{file_prefix}_{timestamp}.json"
                
                if not os.path.exists(file_path):
                    print(f"Warning: Backup file {file_path} not found, skipping.")
                    continue
                
                print(f"Restoring {file_prefix}...")
                
                # Load data from JSON file
                with open(file_path, 'r') as f:
                    items = json.load(f)
                
                if not items:
                    print(f"No {file_prefix} to restore.")
                    continue
                
                # Special handling for users to set passwords
                if file_prefix == 'users':
                    restore_users(items)
                    continue
                
                # Special handling for SMTP configs to set passwords
                if file_prefix == 'smtp_configs':
                    restore_smtp_configs(items)
                    continue
                
                # For other models, create instances from the data
                for item_data in items:
                    # Create new instance and set attributes
                    instance = model_class()
                    for key, value in item_data.items():
                        # Skip ID attribute (let the database assign new IDs)
                        if key == 'id':
                            continue
                        
                        # Convert string dates back to datetime
                        if key.endswith('_at') and value and isinstance(value, str):
                            try:
                                setattr(instance, key, datetime.datetime.fromisoformat(value))
                            except ValueError:
                                # Skip attributes that can't be properly converted
                                print(f"Warning: Could not convert date {value} for {key}")
                        else:
                            setattr(instance, key, value)
                    
                    db.session.add(instance)
                
                db.session.commit()
                print(f"Restored {len(items)} {file_prefix}.")
            
            print("Data restoration completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error restoring data: {str(e)}")
        return False

def restore_users(user_data):
    """Special handling for restoring users with password reset"""
    print("Restoring users...")
    
    for i, user_item in enumerate(user_data):
        # Create new user
        user = User()
        
        # Set basic attributes
        for key, value in user_item.items():
            # Skip ID and sensitive fields
            if key in ('id', 'password_hash'):
                continue
            
            # Convert string dates back to datetime
            if key.endswith('_at') and value and isinstance(value, str):
                try:
                    setattr(user, key, datetime.datetime.fromisoformat(value))
                except ValueError:
                    print(f"Warning: Could not convert date {value} for {key}")
            else:
                setattr(user, key, value)
        
        # Set a default password
        default_password = f"ChangeMe123!_{user.username}"
        user.password_hash = generate_password_hash(default_password)
        
        # Mark as verified
        user.email_verified = True
        user.is_active = True
        
        db.session.add(user)
        print(f"Restored user: {user.username} with default password (will need to be changed)")
    
    db.session.commit()
    print(f"Restored {len(user_data)} users.")
    print("IMPORTANT: All users have been restored with default passwords and will need to be reset.")

def restore_smtp_configs(smtp_data):
    """Special handling for restoring SMTP configs with password prompts"""
    print("Restoring SMTP configurations...")
    
    for i, smtp_item in enumerate(smtp_data):
        # Create new SMTP config
        smtp = SMTPConfig()
        
        # Set basic attributes
        for key, value in smtp_item.items():
            # Skip ID and sensitive fields
            if key in ('id', 'password'):
                continue
            
            # Convert string dates back to datetime
            if key.endswith('_at') and value and isinstance(value, str):
                try:
                    setattr(smtp, key, datetime.datetime.fromisoformat(value))
                except ValueError:
                    print(f"Warning: Could not convert date {value} for {key}")
            else:
                setattr(smtp, key, value)
        
        # Set a placeholder password
        smtp.password = "PLACEHOLDER_UPDATE_THIS"
        
        db.session.add(smtp)
        print(f"Restored SMTP config: {smtp.name} (password will need to be updated)")
    
    db.session.commit()
    print(f"Restored {len(smtp_data)} SMTP configurations.")
    print("IMPORTANT: All SMTP configurations have placeholder passwords and will need to be updated.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        timestamp = sys.argv[1]
        print(f"Using provided timestamp: {timestamp}")
    else:
        timestamp = None
        print("No timestamp provided, using most recent backup.")
    
    print("Starting data restoration...")
    
    if restore_data(timestamp):
        print("Data restoration completed successfully!")
    else:
        print("Data restoration failed.")
        sys.exit(1)