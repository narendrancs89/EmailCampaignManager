import os
import logging
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create a base class for models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///email_campaign.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure Flask-Mail
app.config["MAIL_SERVER"] = "smtp.example.com"  # Default, will be overridden by database config
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = None
app.config["MAIL_PASSWORD"] = None
app.config["MAIL_DEFAULT_SENDER"] = "noreply@yourdomain.com"

# Configure Brevo (for API-based email sending)
app.config["BREVO_API_KEY"] = os.environ.get("BREVO_API_KEY")
app.config["USE_BREVO_API"] = True if os.environ.get("BREVO_API_KEY") else False

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
# login_manager.login_view = 'login'  # Will be set after routes are imported
login_manager.login_message_category = 'info'
mail.init_app(app)

# Add context processor for templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Import models to ensure tables are created
import models  # noqa: F401

# Import routes to register them with the app
import routes  # noqa: F401

# Initialize scheduler
try:
    from scheduler import init_scheduler
    init_scheduler(app)
except ImportError:
    pass  # Scheduler module may not exist yet
