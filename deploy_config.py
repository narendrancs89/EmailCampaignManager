"""
Deployment-specific configuration for production environments.
This handles PostgreSQL compatibility and deployment optimizations.
"""

import os
from datetime import datetime

def configure_for_deployment(app):
    """Configure the app for production deployment."""
    
    # Production-specific SQLAlchemy configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "echo": False,  # Disable SQL logging in production
    }
    
    # Set proper timezone handling for PostgreSQL
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    
    # Production logging configuration
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )
    
    return app