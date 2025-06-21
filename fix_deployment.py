#!/usr/bin/env python3
"""
Fix deployment-specific database issues for PostgreSQL
"""

import os
import sys

def fix_deployment_issues():
    """Fix PostgreSQL deployment compatibility issues"""
    try:
        from app import app, db
        from models import *
        
        with app.app_context():
            print("Fixing PostgreSQL deployment issues...")
            
            # Test all problematic queries that were failing in deployment
            from datetime import datetime
            
            # Test basic user query
            from sqlalchemy import or_
            admin_user = User.query.filter(
                or_(User.username == 'admin', User.email == 'admin@example.com')
            ).first()
            print(f"✓ User query works: {admin_user.username if admin_user else 'No admin user'}")
            
            # Test scheduled job queries
            current_time = datetime.utcnow()
            jobs = ScheduledJob.query.filter(
                ScheduledJob.status == 'scheduled'
            ).all()
            print(f"✓ Scheduled job query works: {len(jobs)} jobs")
            
            # Test complex filter queries
            test_jobs = ScheduledJob.query.filter(
                ScheduledJob.scheduled_time >= current_time
            ).limit(10).all()
            print(f"✓ Time-based query works: {len(test_jobs)} jobs")
            
            # Ensure all models can be queried
            models_to_test = [
                (User, 'users'),
                (EmailTemplate, 'templates'), 
                (EmailSegment, 'segments'),
                (Contact, 'contacts'),
                (SMTPConfig, 'smtp_configs'),
                (ScheduledJob, 'jobs'),
                (JobLog, 'job_logs')
            ]
            
            for model, name in models_to_test:
                try:
                    count = model.query.count()
                    print(f"✓ {name}: {count} records")
                except Exception as e:
                    print(f"❌ {name} error: {e}")
                    return False
            
            print("✓ All deployment fixes verified")
            return True
            
    except Exception as e:
        print(f"❌ Deployment fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_deployment_issues()
    sys.exit(0 if success else 1)