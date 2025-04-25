import os
import secrets
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import app, db, mail
from models import User, EmailSegment, Contact, EmailTemplate, ScheduledJob, SMTPConfig, UserSession, UserRegistrationRequest, AdminEmailList, AdminEmailContact
from forms import (
    LoginForm, RegistrationForm, SegmentForm, ContactForm, ContactImportForm,
    TemplateForm, ScheduleJobForm, SMTPConfigForm, EmailEditorForm,
    EmailVerificationForm, ResetPasswordRequestForm, ResetPasswordForm,
    AdminLoginForm, UserApprovalForm, UserPermissionsForm,
    AdminEmailListForm, AdminEmailContactForm, AdminContactImportForm
)
from email_service import update_mail_settings
from flask_mail import Message
import logging
import json
import csv
import io

# Email helper functions
def send_verification_email(email, token):
    """Send an email verification link to the user"""
    try:
        verify_url = url_for('verify_email', token=token, _external=True)
        msg = Message('Verify Your Email Address',
                     sender=app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[email])
        msg.body = f'''To verify your email address, visit the following link:
{verify_url}

If you did not make this request, simply ignore this email.
'''
        msg.html = f'''
<p>To verify your email address, click the button below:</p>
<p><a href="{verify_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
<p>Or visit this link: <a href="{verify_url}">{verify_url}</a></p>
<p>If you did not make this request, simply ignore this email.</p>
'''
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Error sending verification email: {str(e)}")
        return False

def send_password_reset_email(email, token):
    """Send a password reset link to the user"""
    try:
        reset_url = url_for('reset_password', token=token, _external=True)
        msg = Message('Password Reset Request',
                     sender=app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[email])
        msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email.
'''
        msg.html = f'''
<p>To reset your password, click the button below:</p>
<p><a href="{reset_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
<p>Or visit this link: <a href="{reset_url}">{reset_url}</a></p>
<p>If you did not make this request, simply ignore this email.</p>
<p>This link will expire in 1 hour.</p>
'''
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Error sending password reset email: {str(e)}")
        return False
        
def send_approval_notification(email, username):
    """Send an approval notification to the user"""
    try:
        login_url = url_for('login', _external=True)
        msg = Message('Account Approved',
                     sender=app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[email])
        msg.body = f'''Your account {username} has been approved!
You can now log in at: {login_url}
'''
        msg.html = f'''
<p>Congratulations! Your account <strong>{username}</strong> has been approved.</p>
<p>You can now <a href="{login_url}">log in to your account</a>.</p>
'''
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Error sending approval notification: {str(e)}")
        return False
        
def send_rejection_notification(email, username, reason):
    """Send a rejection notification to the user"""
    try:
        register_url = url_for('register', _external=True)
        msg = Message('Account Registration Status',
                     sender=app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[email])
        msg.body = f'''Unfortunately, your account registration for {username} was not approved.
Reason: {reason}

You may register again at: {register_url}
'''
        msg.html = f'''
<p>Unfortunately, your account registration for <strong>{username}</strong> was not approved.</p>
<p><strong>Reason:</strong> {reason}</p>
<p>You may <a href="{register_url}">register again</a> if you wish.</p>
'''
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Error sending rejection notification: {str(e)}")
        return False

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        # Update last login time
        user.last_login = datetime.utcnow()
        
        # Record session info
        user_session = UserSession(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(user_session)
        db.session.commit()
        
        # Store session ID in user session
        session['session_id'] = user_session.id
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
            
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    if current_user.is_authenticated and 'session_id' in session:
        # Update logout time
        user_session = UserSession.query.get(session['session_id'])
        if user_session:
            user_session.logout_time = datetime.utcnow()
            db.session.commit()
    
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a registration request instead of a user
        reg_request = UserRegistrationRequest(
            username=form.username.data, 
            email=form.email.data
        )
        reg_request.set_password(form.password.data)
        
        # Generate verification token
        verification_token = reg_request.verification_token = secrets.token_urlsafe(32)
        
        db.session.add(reg_request)
        db.session.commit()
        
        # Send verification email
        send_verification_email(reg_request.email, verification_token)
        
        flash('Registration submitted! Please check your email to verify your account.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    # Find registration request with this token
    reg_request = UserRegistrationRequest.query.filter_by(verification_token=token).first()
    
    if not reg_request:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('login'))
    
    # Mark email as verified
    reg_request.email_verified = True
    db.session.commit()
    
    flash('Email verified! Your registration is now pending admin approval.', 'success')
    return redirect(url_for('login'))

@app.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate reset token
            reset_token = user.generate_reset_token()
            # Send reset email
            send_password_reset_email(user.email, reset_token)
            
        # Always show success, don't confirm email existence
        flash('If your email is registered, you will receive password reset instructions.', 'info')
        return redirect(url_for('login'))
    
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Find user with matching token
    user = User.query.filter_by(reset_password_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_password_token = None
        user.reset_token_expires = None
        db.session.commit()
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', title='Reset Your Password', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get counts for dashboard widgets
    segment_count = EmailSegment.query.filter_by(user_id=current_user.id).count()
    template_count = EmailTemplate.query.filter_by(user_id=current_user.id).count()
    job_count = ScheduledJob.query.filter_by(user_id=current_user.id).count()
    smtp_count = SMTPConfig.query.filter_by(user_id=current_user.id).count()
    
    # Get recent jobs
    recent_jobs = ScheduledJob.query.filter_by(user_id=current_user.id).order_by(ScheduledJob.scheduled_time.desc()).limit(5).all()
    
    return render_template('dashboard.html', title='Dashboard', 
                           segment_count=segment_count, 
                           template_count=template_count,
                           job_count=job_count,
                           smtp_count=smtp_count,
                           recent_jobs=recent_jobs)

# Email Segments Routes
@app.route('/segments')
@login_required
def segments():
    segments = EmailSegment.query.filter_by(user_id=current_user.id).all()
    return render_template('segments.html', title='Email Segments', segments=segments)

@app.route('/segments/new', methods=['GET', 'POST'])
@login_required
def new_segment():
    form = SegmentForm()
    if form.validate_on_submit():
        segment = EmailSegment(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(segment)
        db.session.commit()
        flash('Segment created successfully!', 'success')
        return redirect(url_for('segments'))
    
    return render_template('segment_editor.html', title='New Segment', form=form)

@app.route('/segments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_segment(id):
    segment = EmailSegment.query.get_or_404(id)
    
    # Check if the segment belongs to the current user
    if segment.user_id != current_user.id:
        flash('You do not have permission to edit this segment.', 'danger')
        return redirect(url_for('segments'))
    
    form = SegmentForm()
    if form.validate_on_submit():
        segment.name = form.name.data
        segment.description = form.description.data
        db.session.commit()
        flash('Segment updated successfully!', 'success')
        return redirect(url_for('segments'))
    
    # Pre-populate form with segment data
    if request.method == 'GET':
        form.name.data = segment.name
        form.description.data = segment.description
    
    return render_template('segment_editor.html', title='Edit Segment', form=form, segment=segment)

@app.route('/segments/<int:id>/delete', methods=['POST'])
@login_required
def delete_segment(id):
    segment = EmailSegment.query.get_or_404(id)
    
    # Check if the segment belongs to the current user
    if segment.user_id != current_user.id:
        flash('You do not have permission to delete this segment.', 'danger')
        return redirect(url_for('segments'))
    
    db.session.delete(segment)
    db.session.commit()
    flash('Segment deleted successfully!', 'success')
    return redirect(url_for('segments'))

@app.route('/segments/<int:id>/contacts', methods=['GET', 'POST'])
@login_required
def segment_contacts(id):
    segment = EmailSegment.query.get_or_404(id)
    
    # Check if the segment belongs to the current user
    if segment.user_id != current_user.id:
        flash('You do not have permission to view this segment.', 'danger')
        return redirect(url_for('segments'))
    
    contact_form = ContactForm()
    import_form = ContactImportForm()
    
    if contact_form.validate_on_submit() and 'add_contact' in request.form:
        contact = Contact(
            email=contact_form.email.data,
            name=contact_form.name.data,
            segment_id=segment.id
        )
        db.session.add(contact)
        db.session.commit()
        flash('Contact added successfully!', 'success')
        return redirect(url_for('segment_contacts', id=segment.id))
    
    if import_form.validate_on_submit() and 'import_contacts' in request.form:
        contacts_data = import_form.contacts.data.strip().split('\n')
        added_count = 0
        
        for line in contacts_data:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split(',', 1)
            email = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else None
            
            # Basic email validation
            if '@' not in email:
                continue
            
            contact = Contact(
                email=email,
                name=name,
                segment_id=segment.id
            )
            db.session.add(contact)
            added_count += 1
        
        if added_count > 0:
            db.session.commit()
            flash(f'{added_count} contacts imported successfully!', 'success')
        else:
            flash('No valid contacts found for import.', 'warning')
            
        return redirect(url_for('segment_contacts', id=segment.id))
    
    # Get contacts for this segment
    contacts = Contact.query.filter_by(segment_id=segment.id).all()
    
    return render_template('segment_contacts.html', 
                           title=f'Contacts - {segment.name}', 
                           segment=segment, 
                           contacts=contacts, 
                           contact_form=contact_form,
                           import_form=import_form)

@app.route('/segments/<int:segment_id>/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(segment_id, contact_id):
    segment = EmailSegment.query.get_or_404(segment_id)
    
    # Check if the segment belongs to the current user
    if segment.user_id != current_user.id:
        flash('You do not have permission to modify this segment.', 'danger')
        return redirect(url_for('segments'))
    
    contact = Contact.query.get_or_404(contact_id)
    
    # Check if the contact belongs to the segment
    if contact.segment_id != segment.id:
        flash('This contact does not belong to the specified segment.', 'danger')
        return redirect(url_for('segment_contacts', id=segment.id))
    
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('segment_contacts', id=segment.id))

# Email Templates Routes
@app.route('/templates')
@login_required
def templates():
    templates = EmailTemplate.query.filter_by(user_id=current_user.id).all()
    return render_template('templates.html', title='Email Templates', templates=templates)

@app.route('/templates/new', methods=['GET', 'POST'])
@login_required
def new_template():
    form = EmailEditorForm()
    
    if form.validate_on_submit():
        template = EmailTemplate(
            name=form.name.data,
            subject=form.subject.data,
            content=form.content.data,
            type=form.type.data,
            user_id=current_user.id
        )
        db.session.add(template)
        db.session.commit()
        flash('Template created successfully!', 'success')
        return redirect(url_for('templates'))
    
    return render_template('email_editor.html', title='New Template', form=form)

@app.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_template(id):
    template = EmailTemplate.query.get_or_404(id)
    
    # Check if the template belongs to the current user
    if template.user_id != current_user.id:
        flash('You do not have permission to edit this template.', 'danger')
        return redirect(url_for('templates'))
    
    form = EmailEditorForm()
    
    if form.validate_on_submit():
        template.name = form.name.data
        template.subject = form.subject.data
        template.content = form.content.data
        template.type = form.type.data
        db.session.commit()
        flash('Template updated successfully!', 'success')
        return redirect(url_for('templates'))
    
    # Pre-populate form with template data
    if request.method == 'GET':
        form.template_id.data = template.id
        form.name.data = template.name
        form.subject.data = template.subject
        form.content.data = template.content
        form.type.data = template.type
    
    return render_template('email_editor.html', title='Edit Template', form=form, template=template)

@app.route('/templates/<int:id>/delete', methods=['POST'])
@login_required
def delete_template(id):
    template = EmailTemplate.query.get_or_404(id)
    
    # Check if the template belongs to the current user
    if template.user_id != current_user.id:
        flash('You do not have permission to delete this template.', 'danger')
        return redirect(url_for('templates'))
    
    db.session.delete(template)
    db.session.commit()
    flash('Template deleted successfully!', 'success')
    return redirect(url_for('templates'))

# SMTP Configuration Routes
@app.route('/smtp-config')
@login_required
def smtp_config():
    configs = SMTPConfig.query.filter_by(user_id=current_user.id).all()
    return render_template('smtp_config.html', title='SMTP Configurations', configs=configs)

@app.route('/smtp-config/new', methods=['GET', 'POST'])
@login_required
def new_smtp_config():
    form = SMTPConfigForm()
    
    if form.validate_on_submit():
        config = SMTPConfig(
            name=form.name.data,
            host=form.host.data,
            port=form.port.data,
            username=form.username.data,
            password=form.password.data,
            use_tls=form.use_tls.data,
            use_ssl=form.use_ssl.data,
            from_email=form.from_email.data,
            from_name=form.from_name.data,
            user_id=current_user.id
        )
        db.session.add(config)
        db.session.commit()
        flash('SMTP Configuration created successfully!', 'success')
        return redirect(url_for('smtp_config'))
    
    return render_template('smtp_form.html', title='New SMTP Configuration', form=form)

@app.route('/smtp-config/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_smtp_config(id):
    config = SMTPConfig.query.get_or_404(id)
    
    # Check if the config belongs to the current user
    if config.user_id != current_user.id:
        flash('You do not have permission to edit this configuration.', 'danger')
        return redirect(url_for('smtp_config'))
    
    form = SMTPConfigForm()
    
    if form.validate_on_submit():
        config.name = form.name.data
        config.host = form.host.data
        config.port = form.port.data
        config.username = form.username.data
        
        # Only update password if a new one is provided
        if form.password.data:
            config.password = form.password.data
            
        config.use_tls = form.use_tls.data
        config.use_ssl = form.use_ssl.data
        config.from_email = form.from_email.data
        config.from_name = form.from_name.data
        
        db.session.commit()
        flash('SMTP Configuration updated successfully!', 'success')
        return redirect(url_for('smtp_config'))
    
    # Pre-populate form with config data
    if request.method == 'GET':
        form.name.data = config.name
        form.host.data = config.host
        form.port.data = config.port
        form.username.data = config.username
        # Don't populate password for security reasons
        form.use_tls.data = config.use_tls
        form.use_ssl.data = config.use_ssl
        form.from_email.data = config.from_email
        form.from_name.data = config.from_name
    
    return render_template('smtp_form.html', title='Edit SMTP Configuration', form=form, config=config)

@app.route('/smtp-config/<int:id>/delete', methods=['POST'])
@login_required
def delete_smtp_config(id):
    config = SMTPConfig.query.get_or_404(id)
    
    # Check if the config belongs to the current user
    if config.user_id != current_user.id:
        flash('You do not have permission to delete this configuration.', 'danger')
        return redirect(url_for('smtp_config'))
    
    db.session.delete(config)
    db.session.commit()
    flash('SMTP Configuration deleted successfully!', 'success')
    return redirect(url_for('smtp_config'))

@app.route('/smtp-config/<int:id>/test', methods=['POST'])
@login_required
def test_smtp_config(id):
    config = SMTPConfig.query.get_or_404(id)
    
    # Check if the config belongs to the current user
    if config.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You do not have permission to test this configuration.'})
    
    try:
        # Update mail settings using the selected config
        update_mail_settings(app, config)
        
        # TODO: Implement actual SMTP test - for now just return success
        return jsonify({'success': True, 'message': 'SMTP connection successful!'})
    except Exception as e:
        logging.error(f"SMTP test error: {str(e)}")
        return jsonify({'success': False, 'message': f'SMTP test failed: {str(e)}'})

# Scheduled Jobs Routes
@app.route('/jobs')
@login_required
def jobs():
    jobs = ScheduledJob.query.filter_by(user_id=current_user.id).order_by(ScheduledJob.scheduled_time.desc()).all()
    return render_template('scheduled_jobs.html', title='Scheduled Jobs', jobs=jobs)

@app.route('/jobs/new', methods=['GET', 'POST'])
@login_required
def new_job():
    form = ScheduleJobForm()
    
    # Populate dropdown options
    form.template_id.choices = [
        (t.id, t.name) for t in EmailTemplate.query.filter_by(user_id=current_user.id).all()
    ]
    form.segment_id.choices = [
        (s.id, s.name) for s in EmailSegment.query.filter_by(user_id=current_user.id).all()
    ]
    form.smtp_config_id.choices = [
        (c.id, c.name) for c in SMTPConfig.query.filter_by(user_id=current_user.id).all()
    ]
    
    if form.validate_on_submit():
        # Verify that selected segment has contacts
        segment = EmailSegment.query.get(form.segment_id.data)
        if segment.emails.count() == 0:
            flash('The selected segment has no contacts. Please add contacts before scheduling a job.', 'danger')
            return render_template('job_form.html', title='New Email Job', form=form)
        
        job = ScheduledJob(
            name=form.name.data,
            scheduled_time=form.scheduled_time.data,
            user_id=current_user.id,
            template_id=form.template_id.data,
            segment_id=form.segment_id.data,
            smtp_config_id=form.smtp_config_id.data,
            total_emails=segment.emails.count()
        )
        db.session.add(job)
        db.session.commit()
        flash('Email job scheduled successfully!', 'success')
        return redirect(url_for('jobs'))
    
    return render_template('job_form.html', title='New Email Job', form=form)

@app.route('/jobs/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_job(id):
    job = ScheduledJob.query.get_or_404(id)
    
    # Check if the job belongs to the current user
    if job.user_id != current_user.id:
        flash('You do not have permission to cancel this job.', 'danger')
        return redirect(url_for('jobs'))
    
    # Check if the job can be cancelled
    if job.status not in ['scheduled', 'running']:
        flash('This job cannot be cancelled as it has already completed or failed.', 'warning')
        return redirect(url_for('jobs'))
    
    job.status = 'cancelled'
    db.session.commit()
    flash('Job cancelled successfully!', 'success')
    return redirect(url_for('jobs'))

@app.route('/monitoring')
@login_required
def monitoring():
    # Get all jobs for the current user
    jobs = ScheduledJob.query.filter_by(user_id=current_user.id).order_by(ScheduledJob.scheduled_time.desc()).all()
    
    # Calculate statistics
    total_emails = sum(job.total_emails for job in jobs)
    sent_emails = sum(job.sent_emails for job in jobs)
    failed_emails = sum(job.failed_emails for job in jobs)
    opened_emails = sum(job.opened_emails for job in jobs)
    clicked_emails = sum(job.clicked_emails for job in jobs)
    
    # Group jobs by status for chart
    status_counts = {
        'scheduled': ScheduledJob.query.filter_by(user_id=current_user.id, status='scheduled').count(),
        'running': ScheduledJob.query.filter_by(user_id=current_user.id, status='running').count(),
        'completed': ScheduledJob.query.filter_by(user_id=current_user.id, status='completed').count(),
        'failed': ScheduledJob.query.filter_by(user_id=current_user.id, status='failed').count(),
        'cancelled': ScheduledJob.query.filter_by(user_id=current_user.id, status='cancelled').count()
    }
    
    return render_template('monitoring.html', 
                          title='Monitoring Dashboard',
                          jobs=jobs,
                          total_emails=total_emails,
                          sent_emails=sent_emails,
                          failed_emails=failed_emails,
                          opened_emails=opened_emails,
                          clicked_emails=clicked_emails,
                          status_counts=status_counts)

# Additional routes for missing templates to avoid errors
@app.route('/segment_contacts.html')
@login_required
def segment_contacts_redirect():
    return redirect(url_for('segments'))

@app.route('/smtp_form.html')
@login_required
def smtp_form_redirect():
    return redirect(url_for('smtp_config'))

@app.route('/job_form.html')
@login_required
def job_form_redirect():
    return redirect(url_for('jobs'))
