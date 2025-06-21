#!/usr/bin/env python3
"""
Production deployment initialization script.
This ensures proper database setup for deployment environments.
"""

import os
import sys
import time
import logging

def ensure_production_database():
    """Ensure we're using PostgreSQL in production and initialize properly."""
    try:
        database_url = os.environ.get("DATABASE_URL")
        
        if not database_url:
            print("ERROR: DATABASE_URL environment variable not set")
            sys.exit(1)
            
        if "sqlite" in database_url.lower():
            print("ERROR: SQLite detected in production deployment")
            print("DATABASE_URL must point to PostgreSQL database")
            sys.exit(1)
            
        print(f"✓ PostgreSQL database URL configured")
        
        # Test database connectivity
        import psycopg2
        from urllib.parse import urlparse
        
        url = urlparse(database_url)
        
        # Handle postgres:// vs postgresql:// URL scheme
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            os.environ["DATABASE_URL"] = database_url
            print("✓ Updated DATABASE_URL scheme to postgresql://")
        
        # Test connection
        try:
            conn = psycopg2.connect(
                host=url.hostname,
                port=url.port or 5432,
                user=url.username,
                password=url.password,
                database=url.path[1:] if url.path else 'postgres'
            )
            conn.close()
            print("✓ Database connection successful")
        except Exception as e:
            print(f"ERROR: Database connection failed: {e}")
            sys.exit(1)
            
        # Initialize the application database
        from app import app, db
        from models import User
        
        with app.app_context():
            print("Creating database tables...")
            
            # Configure SQLAlchemy for PostgreSQL deployment
            app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                "pool_recycle": 300,
                "pool_pre_ping": True,
                "pool_size": 10,
                "max_overflow": 20,
                "echo": False,  # Disable SQL logging in production
                "connect_args": {
                    "sslmode": "require",
                    "options": "-c timezone=UTC"
                }
            }
            
            db.create_all()
            print("✓ Database tables created")
            
            # Create admin user if needed
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                print("Creating admin user...")
                from werkzeug.security import generate_password_hash
                
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
                print("✓ Admin user created: admin@example.com / Admin123!")
            else:
                print("✓ Admin user already exists")
                
        print("✓ Production database initialization completed")
        return True
        
    except Exception as e:
        print(f"ERROR: Production database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    ensure_production_database()