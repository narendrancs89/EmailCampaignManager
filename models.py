from datetime import datetime, timedelta
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
    
    # Email verification and account status
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    verification_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Password reset
    reset_password_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # User role (regular or admin)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Permissions (JSON stored as string, will be parsed as needed)
    permissions = db.Column(db.Text, default='{}') 
    
    # Relationships
    segments = db.relationship('EmailSegment', backref='owner', lazy='dynamic')
    templates = db.relationship('EmailTemplate', backref='owner', lazy='dynamic')
    scheduled_jobs = db.relationship('ScheduledJob', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        import secrets
        import json
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        return self.verification_token
        
    def generate_reset_token(self):
        import secrets
        self.reset_password_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_password_token
    
    def verify_reset_token(self, token):
        if token != self.reset_password_token:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        return True
    
    def get_permissions(self):
        import json
        try:
            return json.loads(self.permissions)
        except:
            return {}
            
    def set_permissions(self, permissions_dict):
        import json
        self.permissions = json.dumps(permissions_dict)
        
    def has_permission(self, permission):
        if self.is_admin:
            return True
        permissions = self.get_permissions()
        return permissions.get(permission, False)
    
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
    type = db.Column(db.String(100), nullable=False)  # can contain multiple types, comma-separated
    has_click_tracking = db.Column(db.Boolean, default=False)
    has_open_tracking = db.Column(db.Boolean, default=False)
    has_optout = db.Column(db.Boolean, default=False)
    click_tracking_url = db.Column(db.String(500), nullable=True)
    open_tracking_url = db.Column(db.String(500), nullable=True)
    optout_url = db.Column(db.String(500), nullable=True)
    tracking_image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Template version tracking
    is_draft = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('email_template.id'), nullable=True)
    version = db.Column(db.Integer, default=1)
    
    # Relationships
    jobs = db.relationship('ScheduledJob', backref='template', lazy='dynamic')
    versions = db.relationship('EmailTemplate', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def create_copy(self, new_name=None):
        """Create a copy of this template with a new name"""
        from copy import copy
        
        # Create a new instance with the same attributes
        template_copy = EmailTemplate()
        for column in self.__table__.columns:
            if column.name not in ['id', 'created_at', 'updated_at', 'name', 'parent_id', 'version']:
                setattr(template_copy, column.name, getattr(self, column.name))
        
        # Set the new template's name
        if new_name:
            template_copy.name = new_name
        else:
            template_copy.name = f"{self.name} (Copy)"
            
        # Set parent relationship and version
        template_copy.parent_id = self.id
        template_copy.version = self.version + 1
        
        # Reset timestamps
        template_copy.created_at = datetime.utcnow()
        template_copy.updated_at = datetime.utcnow()
        
        return template_copy
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

class ScheduledJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    # scheduled, paused, running, completed, cancelled, failed
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'), nullable=False)
    segment_id = db.Column(db.Integer, db.ForeignKey('email_segment.id'), nullable=False)
    smtp_config_id = db.Column(db.Integer, db.ForeignKey('smtp_config.id'), nullable=False)
    # Custom sender fields that override SMTP configuration
    from_email = db.Column(db.String(120), nullable=True)
    from_name = db.Column(db.String(120), nullable=True)
    
    # Job execution control fields
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    current_batch = db.Column(db.Integer, default=0)
    batch_size = db.Column(db.Integer, default=100)
    
    # Statistics
    total_emails = db.Column(db.Integer, default=0)
    sent_emails = db.Column(db.Integer, default=0)
    failed_emails = db.Column(db.Integer, default=0)
    opened_emails = db.Column(db.Integer, default=0)
    clicked_emails = db.Column(db.Integer, default=0)
    
    # Added timing statistics
    sending_started_at = db.Column(db.DateTime, nullable=True)
    sending_completed_at = db.Column(db.DateTime, nullable=True)
    avg_sending_rate = db.Column(db.Float, default=0.0)  # emails per second
    
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
        
class EmailOpen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('scheduled_job.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    tracking_id = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Relationships
    job = db.relationship('ScheduledJob', backref=db.backref('opens', lazy='dynamic'))
    contact = db.relationship('Contact', backref=db.backref('opens', lazy='dynamic'))
    
    def __repr__(self):
        return f'<EmailOpen {self.id}>'
        
class EmailClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('scheduled_job.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    tracking_id = db.Column(db.String(64), nullable=False)
    url = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Relationships
    job = db.relationship('ScheduledJob', backref=db.backref('clicks', lazy='dynamic'))
    contact = db.relationship('Contact', backref=db.backref('clicks', lazy='dynamic'))
    
    def __repr__(self):
        return f'<EmailClick {self.id}>'

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

class AdminEmailList(db.Model):
    """Email list that only admin can view and manage"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    contacts = db.relationship('AdminEmailContact', backref='list', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='admin_email_lists')
    
    def __repr__(self):
        return f'<AdminEmailList {self.name}>'

class AdminEmailContact(db.Model):
    """Contact in an admin-only email list"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    company = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    additional_data = db.Column(db.Text, nullable=True)  # JSON string for any additional data
    list_id = db.Column(db.Integer, db.ForeignKey('admin_email_list.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminEmailContact {self.email}>'

class UserRegistrationRequest(db.Model):
    """Stores pending user registration requests that need admin approval"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    verification_token = db.Column(db.String(100), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approval_date = db.Column(db.DateTime, nullable=True)
    rejected = db.Column(db.Boolean, default=False)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Relationships
    approver = db.relationship('User', backref='approved_registrations')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def __repr__(self):
        return f'<UserRegistrationRequest {self.username}>'
