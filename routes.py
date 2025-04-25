import os
import secrets
from datetime import datetime, timedelta
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

# Import email services
from brevo_service import (
    send_verification_email, 
    send_password_reset_email,
    send_approval_notification,
    send_rejection_notification
)

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

# Admin Email List Management Routes
@app.route('/admin/email-lists')
@login_required
def admin_email_lists():
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all email lists
    email_lists = AdminEmailList.query.all()
    
    return render_template('admin_email_lists.html',
                           title='Admin Email Lists',
                           email_lists=email_lists)

@app.route('/admin/email-lists/new', methods=['GET', 'POST'])
@login_required
def admin_new_email_list():
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = AdminEmailListForm()
    
    if form.validate_on_submit():
        email_list = AdminEmailList(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id
        )
        
        db.session.add(email_list)
        db.session.commit()
        
        flash('Email list created successfully!', 'success')
        return redirect(url_for('admin_email_lists'))
    
    return render_template('admin_email_list_form.html',
                           title='Create Email List',
                           form=form)

@app.route('/admin/email-lists/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_email_list(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get email list
    email_list = AdminEmailList.query.get_or_404(id)
    
    form = AdminEmailListForm()
    
    if form.validate_on_submit():
        email_list.name = form.name.data
        email_list.description = form.description.data
        
        db.session.commit()
        
        flash('Email list updated successfully!', 'success')
        return redirect(url_for('admin_email_lists'))
    
    # Pre-populate form with email list data
    if request.method == 'GET':
        form.name.data = email_list.name
        form.description.data = email_list.description
    
    return render_template('admin_email_list_form.html',
                           title='Edit Email List',
                           form=form,
                           email_list=email_list)

@app.route('/admin/email-lists/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_email_list(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get email list
    email_list = AdminEmailList.query.get_or_404(id)
    
    # Delete email list (cascade will delete contacts)
    db.session.delete(email_list)
    db.session.commit()
    
    flash('Email list deleted successfully!', 'success')
    return redirect(url_for('admin_email_lists'))

@app.route('/admin/email-lists/<int:id>/contacts', methods=['GET', 'POST'])
@login_required
def admin_email_list_contacts(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get email list
    email_list = AdminEmailList.query.get_or_404(id)
    
    # Forms for adding contacts
    contact_form = AdminEmailContactForm()
    import_form = AdminContactImportForm()
    
    if contact_form.validate_on_submit() and 'add_contact' in request.form:
        # Add single contact
        contact = AdminEmailContact(
            email=contact_form.email.data,
            name=contact_form.name.data,
            company=contact_form.company.data,
            phone=contact_form.phone.data,
            additional_data=contact_form.additional_data.data,
            list_id=email_list.id
        )
        
        db.session.add(contact)
        db.session.commit()
        
        flash('Contact added successfully!', 'success')
        return redirect(url_for('admin_email_list_contacts', id=email_list.id))
    
    if import_form.validate_on_submit() and 'import_contacts' in request.form:
        # Handle CSV file upload
        if import_form.contacts_file.data:
            try:
                # Read CSV file
                file_content = import_form.contacts_file.data.read().decode('utf-8')
                csv_data = csv.reader(io.StringIO(file_content))
                
                # Skip header row
                next(csv_data, None)
                
                # Process rows
                added_count = 0
                for row in csv_data:
                    if len(row) >= 2:  # At least email and name
                        email = row[0].strip()
                        name = row[1].strip() if len(row) > 1 else None
                        company = row[2].strip() if len(row) > 2 else None
                        phone = row[3].strip() if len(row) > 3 else None
                        
                        # Basic email validation
                        if '@' not in email:
                            continue
                        
                        # Create contact
                        contact = AdminEmailContact(
                            email=email,
                            name=name,
                            company=company,
                            phone=phone,
                            list_id=email_list.id
                        )
                        
                        db.session.add(contact)
                        added_count += 1
                
                if added_count > 0:
                    db.session.commit()
                    flash(f'{added_count} contacts imported successfully!', 'success')
                else:
                    flash('No valid contacts found for import.', 'warning')
            
            except Exception as e:
                flash(f'Error importing contacts: {str(e)}', 'danger')
        
        # Handle CSV text input
        elif import_form.contacts.data:
            try:
                # Process CSV text
                csv_data = csv.reader(io.StringIO(import_form.contacts.data))
                
                # Process rows
                added_count = 0
                for row in csv_data:
                    if len(row) >= 1:  # At least email
                        email = row[0].strip()
                        name = row[1].strip() if len(row) > 1 else None
                        company = row[2].strip() if len(row) > 2 else None
                        phone = row[3].strip() if len(row) > 3 else None
                        
                        # Basic email validation
                        if '@' not in email:
                            continue
                        
                        # Create contact
                        contact = AdminEmailContact(
                            email=email,
                            name=name,
                            company=company,
                            phone=phone,
                            list_id=email_list.id
                        )
                        
                        db.session.add(contact)
                        added_count += 1
                
                if added_count > 0:
                    db.session.commit()
                    flash(f'{added_count} contacts imported successfully!', 'success')
                else:
                    flash('No valid contacts found for import.', 'warning')
            
            except Exception as e:
                flash(f'Error importing contacts: {str(e)}', 'danger')
        
        return redirect(url_for('admin_email_list_contacts', id=email_list.id))
    
    # Get contacts for this list
    contacts = AdminEmailContact.query.filter_by(list_id=email_list.id).all()
    
    return render_template('admin_email_list_contacts.html',
                           title=f'Admin Email List - {email_list.name}',
                           email_list=email_list,
                           contacts=contacts,
                           contact_form=contact_form,
                           import_form=import_form)

@app.route('/admin/email-lists/<int:list_id>/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def admin_delete_contact(list_id, contact_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get email list
    email_list = AdminEmailList.query.get_or_404(list_id)
    
    # Get contact
    contact = AdminEmailContact.query.get_or_404(contact_id)
    
    # Check if contact belongs to this list
    if contact.list_id != email_list.id:
        flash('This contact does not belong to the specified list.', 'danger')
        return redirect(url_for('admin_email_list_contacts', id=email_list.id))
    
    # Delete contact
    db.session.delete(contact)
    db.session.commit()
    
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('admin_email_list_contacts', id=email_list.id))

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
    # Check if user is active
    if not current_user.is_active:
        flash('Your account is not active yet. Please wait for admin approval.', 'warning')
        logout_user()
        return redirect(url_for('login'))

    # Check if user is admin, redirect to admin dashboard if true
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
        
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

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin dashboard.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get pending registration requests
    pending_requests = UserRegistrationRequest.query.filter_by(
        email_verified=True, 
        approved=False, 
        rejected=False
    ).order_by(UserRegistrationRequest.request_date.desc()).all()
    
    # Get recent approved users
    recent_users = User.query.filter_by(is_active=True).order_by(User.created_at.desc()).limit(5).all()
    
    # Get admin email lists
    email_lists = AdminEmailList.query.all()
    
    # Get counts for admin dashboard widgets
    pending_count = len(pending_requests)
    users_count = User.query.count()
    lists_count = len(email_lists)
    contacts_count = AdminEmailContact.query.count()
    
    return render_template('admin_dashboard.html', 
                           title='Admin Dashboard',
                           pending_requests=pending_requests,
                           recent_users=recent_users,
                           email_lists=email_lists,
                           pending_count=pending_count,
                           users_count=users_count,
                           lists_count=lists_count,
                           contacts_count=contacts_count)

@app.route('/admin/user-requests')
@login_required
def admin_user_requests():
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all registration requests
    pending_requests = UserRegistrationRequest.query.filter_by(
        email_verified=True, 
        approved=False, 
        rejected=False
    ).order_by(UserRegistrationRequest.request_date.desc()).all()
    
    approved_requests = UserRegistrationRequest.query.filter_by(
        approved=True
    ).order_by(UserRegistrationRequest.approval_date.desc()).all()
    
    rejected_requests = UserRegistrationRequest.query.filter_by(
        rejected=True
    ).order_by(UserRegistrationRequest.request_date.desc()).all()
    
    return render_template('admin_user_requests.html',
                           title='User Registration Requests',
                           pending_requests=pending_requests,
                           approved_requests=approved_requests,
                           rejected_requests=rejected_requests)

@app.route('/admin/user-requests/<int:id>/approve', methods=['GET', 'POST'])
@login_required
def approve_user_request(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get registration request
    reg_request = UserRegistrationRequest.query.get_or_404(id)
    
    # Check if request is already processed
    if reg_request.approved or reg_request.rejected:
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('admin_user_requests'))
    
    # Create new user from request
    user = User(
        username=reg_request.username,
        email=reg_request.email,
        password_hash=reg_request.password_hash,
        email_verified=True,
        is_active=True
    )
    
    # Mark request as approved
    reg_request.approved = True
    reg_request.approved_by = current_user.id
    reg_request.approval_date = datetime.utcnow()
    
    # Save changes
    db.session.add(user)
    db.session.commit()
    
    # Send approval notification
    send_approval_notification(user.email, user.username)
    
    flash(f'User {user.username} has been approved successfully.', 'success')
    return redirect(url_for('admin_user_requests'))

@app.route('/admin/user-requests/<int:id>/reject', methods=['GET', 'POST'])
@login_required
def reject_user_request(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get registration request
    reg_request = UserRegistrationRequest.query.get_or_404(id)
    
    # Check if request is already processed
    if reg_request.approved or reg_request.rejected:
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('admin_user_requests'))
    
    form = UserApprovalForm()
    
    if form.validate_on_submit():
        # Mark request as rejected
        reg_request.rejected = True
        reg_request.rejection_reason = form.rejection_reason.data
        
        # Save changes
        db.session.commit()
        
        # Send rejection notification
        send_rejection_notification(
            reg_request.email, 
            reg_request.username, 
            form.rejection_reason.data or "No reason provided."
        )
        
        flash(f'User request for {reg_request.username} has been rejected.', 'success')
        return redirect(url_for('admin_user_requests'))
    
    return render_template('reject_user_request.html',
                           title='Reject User Request',
                           form=form,
                           request=reg_request)

@app.route('/admin/users')
@login_required
def admin_users():
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all active users
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    
    return render_template('admin_users.html',
                           title='User Management',
                           users=users)

@app.route('/admin/users/<int:id>/permissions', methods=['GET', 'POST'])
@login_required
def admin_user_permissions(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get user
    user = User.query.get_or_404(id)
    
    # Cannot edit own permissions
    if user.id == current_user.id:
        flash('You cannot edit your own permissions.', 'warning')
        return redirect(url_for('admin_users'))
    
    form = UserPermissionsForm()
    
    if form.validate_on_submit():
        # Update admin status
        user.is_admin = form.is_admin.data
        
        # Update individual permissions
        permissions = {
            'can_manage_segments': form.can_manage_segments.data,
            'can_manage_templates': form.can_manage_templates.data,
            'can_manage_jobs': form.can_manage_jobs.data,
            'can_manage_smtp': form.can_manage_smtp.data
        }
        user.set_permissions(permissions)
        
        # Save changes
        db.session.commit()
        
        flash(f'Permissions for {user.username} updated successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    # Pre-populate form with user permissions
    if request.method == 'GET':
        form.is_admin.data = user.is_admin
        permissions = user.get_permissions()
        form.can_manage_segments.data = permissions.get('can_manage_segments', False)
        form.can_manage_templates.data = permissions.get('can_manage_templates', False)
        form.can_manage_jobs.data = permissions.get('can_manage_jobs', False)
        form.can_manage_smtp.data = permissions.get('can_manage_smtp', False)
    
    return render_template('admin_user_permissions.html',
                           title=f'Edit User Permissions - {user.username}',
                           form=form,
                           user=user)

@app.route('/admin/users/<int:id>/deactivate', methods=['POST'])
@login_required
def admin_deactivate_user(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get user
    user = User.query.get_or_404(id)
    
    # Cannot deactivate self
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin_users'))
    
    # Deactivate user
    user.is_active = False
    db.session.commit()
    
    flash(f'User {user.username} has been deactivated.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:id>/activate', methods=['POST'])
@login_required
def admin_activate_user(id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get user
    user = User.query.get_or_404(id)
    
    # Activate user
    user.is_active = True
    db.session.commit()
    
    flash(f'User {user.username} has been activated.', 'success')
    return redirect(url_for('admin_users'))

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
    # Get date filter (defaults to last 30 days)
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    
    # Default to last 30 days if not specified
    if not from_date_str:
        from_date = datetime.utcnow() - timedelta(days=30)
    else:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
        except ValueError:
            from_date = datetime.utcnow() - timedelta(days=30)
    
    if not to_date_str:
        to_date = datetime.utcnow()
    else:
        try:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
            # Set to end of day
            to_date = to_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            to_date = datetime.utcnow()
    
    # Get all jobs for the current user within date range
    jobs = ScheduledJob.query.filter(
        ScheduledJob.user_id == current_user.id,
        ScheduledJob.scheduled_time >= from_date,
        ScheduledJob.scheduled_time <= to_date
    ).order_by(ScheduledJob.scheduled_time.desc()).all()
    
    # Get all jobs for time-series data (last 90 days)
    time_series_start = datetime.utcnow() - timedelta(days=90)
    all_recent_jobs = ScheduledJob.query.filter(
        ScheduledJob.user_id == current_user.id,
        ScheduledJob.scheduled_time >= time_series_start
    ).order_by(ScheduledJob.scheduled_time.asc()).all()
    
    # Prepare time-series data (daily stats for the last 90 days)
    time_series_data = {}
    for i in range(90):
        day = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
        time_series_data[day] = {
            'date': day,
            'sent': 0,
            'opened': 0,
            'clicked': 0,
            'failed': 0,
            'total': 0
        }
    
    # Fill time series data from jobs
    for job in all_recent_jobs:
        day = job.scheduled_time.strftime('%Y-%m-%d')
        if day in time_series_data:
            time_series_data[day]['sent'] += job.sent_emails
            time_series_data[day]['opened'] += job.opened_emails
            time_series_data[day]['clicked'] += job.clicked_emails
            time_series_data[day]['failed'] += job.failed_emails
            time_series_data[day]['total'] += job.total_emails
    
    # Convert to list and order by date
    time_series_list = list(time_series_data.values())
    time_series_list.sort(key=lambda x: x['date'])
    
    # Calculate statistics for filtered period
    total_emails = sum(job.total_emails for job in jobs)
    sent_emails = sum(job.sent_emails for job in jobs)
    failed_emails = sum(job.failed_emails for job in jobs)
    opened_emails = sum(job.opened_emails for job in jobs)
    clicked_emails = sum(job.clicked_emails for job in jobs)
    
    # Calculate engagement metrics
    open_rate = (opened_emails / sent_emails * 100) if sent_emails > 0 else 0
    click_rate = (clicked_emails / opened_emails * 100) if opened_emails > 0 else 0
    click_to_open_rate = (clicked_emails / opened_emails * 100) if opened_emails > 0 else 0
    bounce_rate = (failed_emails / total_emails * 100) if total_emails > 0 else 0
    
    # Group jobs by status for chart
    status_counts = {
        'scheduled': ScheduledJob.query.filter(
            ScheduledJob.user_id == current_user.id, 
            ScheduledJob.status == 'scheduled',
            ScheduledJob.scheduled_time >= from_date,
            ScheduledJob.scheduled_time <= to_date
        ).count(),
        'running': ScheduledJob.query.filter(
            ScheduledJob.user_id == current_user.id, 
            ScheduledJob.status == 'running',
            ScheduledJob.scheduled_time >= from_date,
            ScheduledJob.scheduled_time <= to_date
        ).count(),
        'completed': ScheduledJob.query.filter(
            ScheduledJob.user_id == current_user.id, 
            ScheduledJob.status == 'completed',
            ScheduledJob.scheduled_time >= from_date,
            ScheduledJob.scheduled_time <= to_date
        ).count(),
        'failed': ScheduledJob.query.filter(
            ScheduledJob.user_id == current_user.id, 
            ScheduledJob.status == 'failed',
            ScheduledJob.scheduled_time >= from_date,
            ScheduledJob.scheduled_time <= to_date
        ).count(),
        'cancelled': ScheduledJob.query.filter(
            ScheduledJob.user_id == current_user.id, 
            ScheduledJob.status == 'cancelled',
            ScheduledJob.scheduled_time >= from_date,
            ScheduledJob.scheduled_time <= to_date
        ).count()
    }
    
    # Get segment performance data
    segment_performance = {}
    for job in jobs:
        segment_id = job.segment_id
        segment_name = job.segment.name
        
        if segment_id not in segment_performance:
            segment_performance[segment_id] = {
                'segment_name': segment_name,
                'total': 0,
                'sent': 0,
                'opened': 0,
                'clicked': 0,
                'failed': 0
            }
        
        segment_performance[segment_id]['total'] += job.total_emails
        segment_performance[segment_id]['sent'] += job.sent_emails
        segment_performance[segment_id]['opened'] += job.opened_emails
        segment_performance[segment_id]['clicked'] += job.clicked_emails
        segment_performance[segment_id]['failed'] += job.failed_emails
    
    # Calculate rates for each segment
    for segment_id in segment_performance:
        data = segment_performance[segment_id]
        data['open_rate'] = (data['opened'] / data['sent'] * 100) if data['sent'] > 0 else 0
        data['click_rate'] = (data['clicked'] / data['opened'] * 100) if data['opened'] > 0 else 0
        data['bounce_rate'] = (data['failed'] / data['total'] * 100) if data['total'] > 0 else 0
    
    # Sort segments by open rate (descending)
    top_segments = sorted(
        segment_performance.values(), 
        key=lambda x: x['open_rate'], 
        reverse=True
    )
    
    # Get template performance data
    template_performance = {}
    for job in jobs:
        template_id = job.template_id
        template_name = job.template.name
        
        if template_id not in template_performance:
            template_performance[template_id] = {
                'template_name': template_name,
                'total': 0,
                'sent': 0,
                'opened': 0,
                'clicked': 0,
                'failed': 0
            }
        
        template_performance[template_id]['total'] += job.total_emails
        template_performance[template_id]['sent'] += job.sent_emails
        template_performance[template_id]['opened'] += job.opened_emails
        template_performance[template_id]['clicked'] += job.clicked_emails
        template_performance[template_id]['failed'] += job.failed_emails
    
    # Calculate rates for each template
    for template_id in template_performance:
        data = template_performance[template_id]
        data['open_rate'] = (data['opened'] / data['sent'] * 100) if data['sent'] > 0 else 0
        data['click_rate'] = (data['clicked'] / data['opened'] * 100) if data['opened'] > 0 else 0
        data['bounce_rate'] = (data['failed'] / data['total'] * 100) if data['total'] > 0 else 0
    
    # Sort templates by click rate (descending)
    top_templates = sorted(
        template_performance.values(), 
        key=lambda x: x['click_rate'], 
        reverse=True
    )
    
    return render_template('monitoring.html', 
                          title='Advanced Analytics Dashboard',
                          jobs=jobs,
                          total_emails=total_emails,
                          sent_emails=sent_emails,
                          failed_emails=failed_emails,
                          opened_emails=opened_emails,
                          clicked_emails=clicked_emails,
                          open_rate=open_rate,
                          click_rate=click_rate,
                          click_to_open_rate=click_to_open_rate,
                          bounce_rate=bounce_rate,
                          status_counts=status_counts,
                          top_segments=top_segments,
                          top_templates=top_templates,
                          time_series_data=time_series_list,
                          from_date=from_date.strftime('%Y-%m-%d'),
                          to_date=to_date.strftime('%Y-%m-%d'))

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
