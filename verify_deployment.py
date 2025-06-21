#!/usr/bin/env python3
"""
Deployment verification script for the email marketing platform.
This script verifies that all components are working correctly.
"""

import sys
import os
from datetime import datetime

def verify_app():
    """Verify the application components."""
    try:
        print("Verifying application components...")
        
        # Test database connection
        from app import app, db
        from models import User, ScheduledJob
        
        with app.app_context():
            print("✓ Database connection successful")
            
            # Test query syntax that was causing deployment issues
            current_time = datetime.utcnow()
            jobs = ScheduledJob.query.filter(
                ScheduledJob.status == 'scheduled'
            ).filter(
                ScheduledJob.scheduled_time > current_time
            ).all()
            print(f"✓ Scheduler query syntax working - found {len(jobs)} jobs")
            
            # Test login query syntax
            test_user = User.query.filter(
                db.or_(User.username == 'admin', User.email == 'admin@example.com')
            ).first()
            if test_user:
                print("✓ Login query syntax working - admin user found")
            else:
                print("⚠ Admin user not found")
            
            # Test database tables
            from sqlalchemy import text
            tables = ['user', 'email_segment', 'contact', 'email_template', 
                     'scheduled_job', 'smtp_config', 'job_log']
            for table in tables:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"✓ Table '{table}' exists with {count} records")
            
        print("\n✓ All verification checks passed!")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_app()
    sys.exit(0 if success else 1)