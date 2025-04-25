from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateTimeField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from models import User

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
        if user is not None:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

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
