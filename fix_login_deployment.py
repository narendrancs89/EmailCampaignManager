#!/usr/bin/env python3
"""
Fix login deployment issues for production
"""

import os
import sys

def fix_login_issues():
    """Fix login authentication issues in deployment"""
    try:
        from app import app, db
        from models import User
        from werkzeug.security import generate_password_hash
        from sqlalchemy import or_
        
        with app.app_context():
            print("Fixing login deployment issues...")
            
            # Ensure admin user exists with correct credentials
            admin_user = User.query.filter(
                or_(User.username == 'admin', User.email == 'admin@example.com')
            ).first()
            
            if not admin_user:
                print("Creating admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('Admin123!'),
                    is_admin=True,
                    email_verified=True,
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created")
            else:
                # Update admin user to ensure correct settings
                admin_user.password_hash = generate_password_hash('Admin123!')
                admin_user.is_admin = True
                admin_user.email_verified = True
                admin_user.is_active = True
                db.session.commit()
                print("✓ Admin user updated")
            
            # Test login functionality
            test_user = User.query.filter(
                or_(User.username == 'admin', User.email == 'admin@example.com')
            ).first()
            
            if test_user and test_user.check_password('Admin123!'):
                print("✓ Login authentication works")
                print(f"✓ Username: {test_user.username}")
                print(f"✓ Email: {test_user.email}")
                print(f"✓ Is Admin: {test_user.is_admin}")
                print(f"✓ Is Active: {test_user.is_active}")
                print(f"✓ Email Verified: {test_user.email_verified}")
            else:
                print("❌ Login authentication failed")
                return False
            
            print("✓ All login fixes completed")
            return True
            
    except Exception as e:
        print(f"❌ Login fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_login_issues()
    sys.exit(0 if success else 1)