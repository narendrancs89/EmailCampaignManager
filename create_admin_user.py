import os
import sys
from app import app, db
from models import User
from datetime import datetime
import json

def create_admin_user():
    """Create a default admin user for testing purposes"""
    with app.app_context():
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create new admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            email_verified=True,
            is_active=True,
            is_admin=True,
            created_at=datetime.utcnow(),
        )
        
        # Set password
        admin_user.set_password('Admin123!')
        
        # Set permissions
        permissions = {
            'can_manage_segments': True,
            'can_manage_templates': True,
            'can_manage_jobs': True,
            'can_manage_smtp': True,
            'can_approve_users': True
        }
        admin_user.permissions = json.dumps(permissions)
        
        # Add to database
        db.session.add(admin_user)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: Admin123!")

if __name__ == '__main__':
    create_admin_user()