from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateTimeField, IntegerField, HiddenField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, URL
from models import User, UserRegistrationRequest

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
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
    
class AdminUserCreationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Admin Access')
    can_manage_segments = BooleanField('Can Manage Segments', default=True)
    can_manage_templates = BooleanField('Can Manage Templates', default=True)
    can_manage_jobs = BooleanField('Can Schedule Jobs', default=True)
    can_manage_smtp = BooleanField('Can Manage SMTP Configs')
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        # Check if username already exists in User table
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already in use. Please choose a different one.')
        
        # Also check pending registration requests
        req = UserRegistrationRequest.query.filter_by(username=username.data).first()
        if req is not None:
            raise ValidationError('Username already in a pending registration request.')
            
    def validate_email(self, email):
        # Check if email already exists in User table
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different one.')
        
        # Also check pending registration requests
        req = UserRegistrationRequest.query.filter_by(email=email.data).first()
        if req is not None:
            raise ValidationError('Email already in a pending registration request.')
    
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
        ('standard', 'Standard Email'),
        ('newsletter', 'Newsletter'),
        ('promotional', 'Promotional'),
        ('transactional', 'Transactional')
    ], validators=[DataRequired()])
    has_click_tracking = BooleanField('Enable Click Tracking')
    has_open_tracking = BooleanField('Enable Open Tracking')
    has_optout = BooleanField('Include Unsubscribe Link')
    template_id = HiddenField('Template ID')
    submit = SubmitField('Save Template')

class ScheduleJobForm(FlaskForm):
    name = StringField('Job Name', validators=[DataRequired(), Length(max=100)])
    template_id = SelectField('Email Template', coerce=int, validators=[DataRequired()])
    segment_id = SelectField('Email Segment', coerce=int, validators=[DataRequired()])
    smtp_config_id = SelectField('SMTP Configuration', coerce=int, validators=[DataRequired()])
    scheduled_time = DateTimeField('Schedule Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    from_email = StringField('From Email', validators=[Optional(), Email()],
                           description='Override the default sender email in SMTP configuration')
    from_name = StringField('From Name', validators=[Optional(), Length(max=120)],
                         description='Override the default sender name in SMTP configuration')
    
    # Optimal send time fields
    use_optimal_time = BooleanField('Use Smart Scheduling', 
                                   description='Automatically adjust sending time to maximize engagement')
    optimal_time_window_start = IntegerField('Earliest Hour (24h)', default=9, validators=[Optional()],
                                          description='Earliest hour to send (24-hour format, e.g. 9 for 9 AM)')
    optimal_time_window_end = IntegerField('Latest Hour (24h)', default=17, validators=[Optional()],
                                        description='Latest hour to send (24-hour format, e.g. 17 for 5 PM)')
    optimal_day_preference = SelectField('Day Preference',
                               choices=[
                                   ('any', 'Any Day'),
                                   ('weekday', 'Weekdays Only'),
                                   ('weekend', 'Weekends Only')
                               ], default='weekday', validators=[Optional()],
                               description='Preferred days for sending emails')
    
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
    
    # Replace SelectField with individual checkboxes
    has_click_tracking = BooleanField('Click Tracking')
    has_open_tracking = BooleanField('Open Tracking')
    has_optout = BooleanField('Unsubscribe Option')
    
    # Add URL fields for tracking and opt-out
    click_tracking_url = StringField('Click Tracking URL', validators=[Optional(), URL()])
    open_tracking_url = StringField('Open Tracking URL', validators=[Optional(), URL()])
    optout_url = StringField('Unsubscribe URL', validators=[Optional(), URL()])
    tracking_image_url = StringField('Tracking Pixel Image URL', validators=[Optional(), URL()])
    
    # Keep the type field for backward compatibility but make it hidden
    type = HiddenField('Template Type')
    
    submit = SubmitField('Save Template')

class TestEmailForm(FlaskForm):
    recipient_email = StringField('Email', validators=[DataRequired(), Email()], 
                                 description='Enter an email address to send a test version of this template')
    smtp_config_id = SelectField('SMTP Configuration', coerce=int, validators=[DataRequired()],
                               description='Select the SMTP configuration to use for sending the test')
    submit = SubmitField('Send Test Email')
