from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    segments = db.relationship('EmailSegment', backref='owner', lazy='dynamic')
    templates = db.relationship('EmailTemplate', backref='owner', lazy='dynamic')
    scheduled_jobs = db.relationship('ScheduledJob', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class EmailSegment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    emails = db.relationship('Contact', backref='segment', lazy='dynamic', cascade='all, delete-orphan')
    jobs = db.relationship('ScheduledJob', backref='segment', lazy='dynamic')
    
    def __repr__(self):
        return f'<EmailSegment {self.name}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    segment_id = db.Column(db.Integer, db.ForeignKey('email_segment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.email}>'

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'click', 'opens', 'optout'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    jobs = db.relationship('ScheduledJob', backref='template', lazy='dynamic')
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

class ScheduledJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'), nullable=False)
    segment_id = db.Column(db.Integer, db.ForeignKey('email_segment.id'), nullable=False)
    smtp_config_id = db.Column(db.Integer, db.ForeignKey('smtp_config.id'), nullable=False)
    
    # Statistics
    total_emails = db.Column(db.Integer, default=0)
    sent_emails = db.Column(db.Integer, default=0)
    failed_emails = db.Column(db.Integer, default=0)
    opened_emails = db.Column(db.Integer, default=0)
    clicked_emails = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ScheduledJob {self.name}>'

class JobLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('scheduled_job.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), default='info')  # info, warning, error
    
    # Relationship
    job = db.relationship('ScheduledJob', backref=db.backref('logs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<JobLog {self.id}>'

class SMTPConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    use_tls = db.Column(db.Boolean, default=True)
    use_ssl = db.Column(db.Boolean, default=False)
    from_email = db.Column(db.String(120), nullable=False)
    from_name = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    jobs = db.relationship('ScheduledJob', backref='smtp_config', lazy='dynamic')
    
    def __repr__(self):
        return f'<SMTPConfig {self.name}>'

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('sessions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<UserSession {self.id}>'
