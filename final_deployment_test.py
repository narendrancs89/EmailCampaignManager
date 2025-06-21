#!/usr/bin/env python3
"""
Final deployment verification script to ensure all components work correctly.
"""

import sys
import os
from datetime import datetime, timedelta

def test_all_components():
    """Test all application components for deployment readiness."""
    try:
        print("🔍 Running comprehensive deployment verification...")
        
        from app import app, db
        from models import User, ScheduledJob, EmailTemplate, EmailSegment, Contact, SMTPConfig
        
        with app.app_context():
            print("✓ Application initialization successful")
            
            # Test all problematic query patterns that were causing deployment failures
            current_time = datetime.utcnow()
            
            # Test scheduler queries (fixed)
            jobs = ScheduledJob.query.filter(
                ScheduledJob.status == 'scheduled'
            ).filter(
                ScheduledJob.scheduled_time > current_time
            ).all()
            print(f"✓ Scheduler query syntax verified - {len(jobs)} scheduled jobs")
            
            # Test analytics queries (fixed)
            from_date = current_time - timedelta(days=30)
            to_date = current_time
            
            # Test the complex queries that were failing in deployment
            test_jobs = ScheduledJob.query.filter(
                ScheduledJob.scheduled_time >= from_date
            ).filter(
                ScheduledJob.scheduled_time <= to_date
            ).all()
            print(f"✓ Analytics query syntax verified - {len(test_jobs)} jobs in range")
            
            # Test status-based queries (fixed)
            status_counts = {
                'scheduled': ScheduledJob.query.filter(
                    ScheduledJob.status == 'scheduled'
                ).filter(
                    ScheduledJob.scheduled_time >= from_date
                ).filter(
                    ScheduledJob.scheduled_time <= to_date
                ).count(),
                'completed': ScheduledJob.query.filter(
                    ScheduledJob.status == 'completed'
                ).filter(
                    ScheduledJob.scheduled_time >= from_date
                ).filter(
                    ScheduledJob.scheduled_time <= to_date
                ).count()
            }
            print(f"✓ Status query syntax verified - {sum(status_counts.values())} total status queries")
            
            # Test login query (fixed)
            from sqlalchemy import or_
            admin_user = User.query.filter(
                or_(User.username == 'admin', User.email == 'admin@example.com')
            ).first()
            print(f"✓ Login query syntax verified - admin user: {admin_user.username if admin_user else 'not found'}")
            
            # Test database tables exist
            tables = [User, EmailTemplate, EmailSegment, Contact, SMTPConfig, ScheduledJob]
            for model in tables:
                count = model.query.count()
                print(f"✓ Table {model.__tablename__} verified - {count} records")
            
            print("\n🎉 All deployment verification tests passed!")
            print("🚀 Application is ready for production deployment!")
            
        return True
        
    except Exception as e:
        print(f"❌ Deployment verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_all_components()
    if success:
        print("\n✅ DEPLOYMENT READY: All systems verified")
        sys.exit(0)
    else:
        print("\n❌ DEPLOYMENT BLOCKED: Issues detected")
        sys.exit(1)