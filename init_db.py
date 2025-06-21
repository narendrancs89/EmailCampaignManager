#!/usr/bin/env python3
"""
Database initialization script for the email campaign platform.
This script creates the database tables and sets up a default admin user.
"""

from app import app, db
from models import User

def init_database():
    """Initialize the database with tables and default data."""
    with app.app_context():
        try:
            # Create all database tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully.")
            
            # Create a default admin user if none exists
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                print("Creating default admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    email_verified=True,
                    is_active=True
                )
                admin_user.set_password('Admin123!')
                db.session.add(admin_user)
                db.session.commit()
                print('Created default admin user: admin@example.com / Admin123!')
            else:
                print("Admin user already exists.")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
    
    return True

if __name__ == '__main__':
    success = init_database()
    if success:
        print("Database initialization completed successfully.")
    else:
        print("Database initialization failed.")