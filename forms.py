from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateTimeField, IntegerField, HiddenField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from models import User, UserRegistrationRequest

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        request = UserRegistrationRequest.query.filter_by(username=username.data).first()
        
        if user is not None or request is not None:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        request = UserRegistrationRequest.query.filter_by(email=email.data).first()
        
        if user is not None or request is not None:
            raise ValidationError('Please use a different email address.')

class EmailVerificationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    token = StringField('Verification Token', validators=[DataRequired()])
    submit = SubmitField('Verify Email')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class AdminLoginForm(FlaskForm):
    username = StringField('Admin Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Admin Sign In')

class UserApprovalForm(FlaskForm):
    approve = SubmitField('Approve')
    reject = SubmitField('Reject')
    rejection_reason = TextAreaField('Rejection Reason')

class UserPermissionsForm(FlaskForm):
    is_admin = BooleanField('Admin Access')
    can_manage_segments = BooleanField('Can Manage Segments')
    can_manage_templates = BooleanField('Can Manage Templates')
    can_manage_jobs = BooleanField('Can Schedule Jobs')
    can_manage_smtp = BooleanField('Can Manage SMTP Configs')
    submit = SubmitField('Update Permissions')
    
class AdminEmailListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Email List')

class AdminEmailContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[Optional(), Length(max=120)])
    company = StringField('Company', validators=[Optional(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=50)])
    additional_data = TextAreaField('Additional Data (JSON)', validators=[Optional()])
    submit = SubmitField('Add Contact')

class AdminContactImportForm(FlaskForm):
    contacts_file = FileField('CSV File', validators=[Optional()])
    contacts = TextAreaField('Contacts (CSV format)', validators=[Optional()])
    submit = SubmitField('Import Contacts')

class SegmentForm(FlaskForm):
    name = StringField('Segment Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Segment')

class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[Optional(), Length(max=120)])
    submit = SubmitField('Add Contact')

class ContactImportForm(FlaskForm):
    contacts = TextAreaField('Contacts (one email per line, format: email,name)', validators=[DataRequired()])
    submit = SubmitField('Import Contacts')

class TemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(max=100)])
    subject = StringField('Email Subject', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Email Content', validators=[DataRequired()])
    type = SelectField('Template Type', choices=[
        ('click', 'Click Tracking'), 
        ('open', 'Open Tracking'), 
        ('optout', 'Opt-out Template')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Template')

class ScheduleJobForm(FlaskForm):
    name = StringField('Job Name', validators=[DataRequired(), Length(max=100)])
    template_id = SelectField('Email Template', coerce=int, validators=[DataRequired()])
    segment_id = SelectField('Email Segment', coerce=int, validators=[DataRequired()])
    smtp_config_id = SelectField('SMTP Configuration', coerce=int, validators=[DataRequired()])
    scheduled_time = DateTimeField('Schedule Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    submit = SubmitField('Schedule Job')

class SMTPConfigForm(FlaskForm):
    name = StringField('Configuration Name', validators=[DataRequired(), Length(max=100)])
    host = StringField('SMTP Host', validators=[DataRequired(), Length(max=100)])
    port = IntegerField('SMTP Port', validators=[DataRequired()])
    username = StringField('SMTP Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('SMTP Password', validators=[DataRequired(), Length(max=256)])
    use_tls = BooleanField('Use TLS', default=True)
    use_ssl = BooleanField('Use SSL')
    from_email = StringField('From Email', validators=[DataRequired(), Email()])
    from_name = StringField('From Name', validators=[Optional(), Length(max=120)])
    submit = SubmitField('Save Configuration')

class EmailEditorForm(FlaskForm):
    template_id = HiddenField('Template ID')
    name = StringField('Template Name', validators=[DataRequired(), Length(max=100)])
    subject = StringField('Email Subject', validators=[DataRequired(), Length(max=200)])
    content = HiddenField('Email Content', validators=[DataRequired()])
    type = SelectField('Template Type', choices=[
        ('click', 'Click Tracking'), 
        ('open', 'Open Tracking'), 
        ('optout', 'Opt-out Template')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Template')
