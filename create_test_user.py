import os
import sys
from app import app, db
from models import User
from datetime import datetime
import json

def create_test_user():
    """Create a regular test user for testing purposes"""
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print("Test user already exists!")
            return
        
        # Create new test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            email_verified=True,
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
        )
        
        # Set password
        test_user.set_password('Test123!')
        
        # Set permissions
        permissions = {
            'can_manage_segments': True,
            'can_manage_templates': True,
            'can_manage_jobs': True,
            'can_manage_smtp': True
        }
        test_user.permissions = json.dumps(permissions)
        
        # Add to database
        db.session.add(test_user)
        db.session.commit()
        
        print("Test user created successfully!")
        print("Username: testuser")
        print("Password: Test123!")

if __name__ == '__main__':
    create_test_user()