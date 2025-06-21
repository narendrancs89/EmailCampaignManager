#!/usr/bin/env python3
"""
Database initialization script for the email campaign platform.
This script creates the database tables and sets up a default admin user.
"""

import os
import sys

def init_database():
    """Initialize the database with tables and default data."""
    try:
        from app import app, db
        from models import User
        
        with app.app_context():
            # Create all database tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully.")
            
            # Create a default admin user if none exists
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                print("Creating default admin user...")
                admin_user = User()
                admin_user.username = 'admin'
                admin_user.email = 'admin@example.com'
                admin_user.is_admin = True
                admin_user.email_verified = True
                admin_user.is_active = True
                admin_user.set_password('Admin123!')
                
                db.session.add(admin_user)
                db.session.commit()
                print('Created default admin user: admin@example.com / Admin123!')
            else:
                print("Admin user already exists.")
                
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = init_database()
    if success:
        print("Database initialization completed successfully.")
        sys.exit(0)
    else:
        print("Database initialization failed.")
        sys.exit(1)