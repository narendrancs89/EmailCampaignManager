import logging
from flask_mail import Mail, Message
from models import ScheduledJob, SMTPConfig, EmailSegment, EmailTemplate, Contact, JobLog
from app import db, mail
import time
from bs4 import BeautifulSoup
import uuid
import traceback
from datetime import datetime

def update_mail_settings(app, smtp_config):
    """Update Flask-Mail settings based on SMTP configuration"""
    app.config['MAIL_SERVER'] = smtp_config.host
    app.config['MAIL_PORT'] = smtp_config.port
    app.config['MAIL_USERNAME'] = smtp_config.username
    app.config['MAIL_PASSWORD'] = smtp_config.password
    app.config['MAIL_USE_TLS'] = smtp_config.use_tls
    app.config['MAIL_USE_SSL'] = smtp_config.use_ssl
    app.config['MAIL_DEFAULT_SENDER'] = (smtp_config.from_name, smtp_config.from_email) if smtp_config.from_name else smtp_config.from_email
    
    # Reinitialize mail with new settings
    global mail
    mail = Mail(app)
    
    logging.info(f"Mail settings updated for SMTP server: {smtp_config.host}")
    return True

def send_campaign_emails(app, job):
    """Send emails for a campaign job"""
    try:
        # Get associated resources
        template = EmailTemplate.query.get(job.template_id)
        segment = EmailSegment.query.get(job.segment_id)
        smtp_config = SMTPConfig.query.get(job.smtp_config_id)
        
        if not template or not segment or not smtp_config:
            log_entry = JobLog(job_id=job.id, message="Missing template, segment, or SMTP configuration", level='error')
            db.session.add(log_entry)
            db.session.commit()
            return False, 0, 0, 0
        
        # Update mail settings
        update_mail_settings(app, smtp_config)
        
        # Get contacts for this segment
        contacts = Contact.query.filter_by(segment_id=segment.id).all()
        
        total = len(contacts)
        sent = 0
        failed = 0
        
        # Log start of sending
        log_entry = JobLog(job_id=job.id, message=f"Starting to send {total} emails", level='info')
        db.session.add(log_entry)
        db.session.commit()
        
        # Send emails to each contact
        for contact in contacts:
            try:
                # Personalize the email content
                personalized_content = personalize_email(template.content, contact)
                
                # Add tracking if enabled for this template
                if template.has_open_tracking:
                    personalized_content = add_open_tracking(personalized_content, job.id, contact.id)
                
                if template.has_click_tracking:
                    personalized_content = add_click_tracking(personalized_content, job.id, contact.id)
                
                # Set the sender (use custom sender if available, otherwise use SMTP config)
                sender_email = job.from_email if job.from_email else smtp_config.from_email
                sender_name = job.from_name if job.from_name else smtp_config.from_name
                sender = f"{sender_name} <{sender_email}>" if sender_name else sender_email
                
                # Create the email message
                msg = Message(
                    subject=template.subject,
                    recipients=[contact.email],
                    html=personalized_content,
                    sender=sender
                )
                
                # Send the email
                mail.send(msg)
                sent += 1
                
                # Add small delay to avoid overloading the SMTP server
                time.sleep(0.1)
                
            except Exception as e:
                logging.error(f"Error sending email to {contact.email}: {str(e)}")
                failed += 1
                
                # Log the error
                error_msg = f"Failed to send email to {contact.email}: {str(e)}"
                log_entry = JobLog(job_id=job.id, message=error_msg, level='error')
                db.session.add(log_entry)
                db.session.commit()
        
        # Log completion
        log_entry = JobLog(
            job_id=job.id, 
            message=f"Email sending completed. Total: {total}, Sent: {sent}, Failed: {failed}", 
            level='info'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return True, total, sent, failed
    
    except Exception as e:
        logging.error(f"Error in send_campaign_emails: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Log the error
        log_entry = JobLog(job_id=job.id, message=f"Email campaign failed: {str(e)}", level='error')
        db.session.add(log_entry)
        db.session.commit()
        
        return False, 0, 0, job.total_emails

def personalize_email(content, contact):
    """Replace personalization tokens in email content"""
    personalized = content
    
    # Replace name if available
    if contact.name:
        personalized = personalized.replace('{{name}}', contact.name)
    else:
        personalized = personalized.replace('{{name}}', 'Valued Customer')
    
    # Replace email
    personalized = personalized.replace('{{email}}', contact.email)
    
    return personalized

def add_open_tracking(content, job_id, contact_id):
    """Add open tracking pixel to email"""
    # Create a tracking pixel
    tracking_id = str(uuid.uuid4())
    
    # Use request.url_root to get the domain of the current application
    # For now, we'll use a relative URL which will resolve correctly 
    # regardless of the domain the application is deployed on
    tracking_pixel = f'<img src="/track/open/{job_id}/{contact_id}/{tracking_id}" width="1" height="1" alt="" style="display:none" />'
    
    # Add tracking pixel before closing body tag
    if '</body>' in content:
        return content.replace('</body>', f'{tracking_pixel}</body>')
    else:
        return content + tracking_pixel

def add_click_tracking(content, job_id, contact_id):
    """Add click tracking to all links in the email"""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all links
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            original_url = link['href']
            # Skip empty or javascript links
            if not original_url or original_url.startswith('javascript:') or original_url.startswith('#'):
                continue
                
            tracking_id = str(uuid.uuid4())
            
            # Use a relative URL which will resolve correctly regardless of the domain
            tracked_url = f"/track/click/{job_id}/{contact_id}/{tracking_id}?url={original_url}"
            link['href'] = tracked_url
    
    return str(soup)

def send_test_email(app, template_id, recipient_email, smtp_config_id):
    """
    Sends a test email using the specified template to the recipient
    
    Args:
        app: Flask application instance
        template_id: ID of the template to use
        recipient_email: Email address to send the test to
        smtp_config_id: ID of the SMTP configuration to use
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Get the template and SMTP configuration
        template = EmailTemplate.query.get(template_id)
        smtp_config = SMTPConfig.query.get(smtp_config_id)
        
        if not template or not smtp_config:
            return False, "Template or SMTP configuration not found"
        
        # Update mail settings for this test
        update_mail_settings(app, smtp_config)
        
        # Create sample data for personalization
        sample_contact = {
            'name': 'Sample Recipient',
            'email': recipient_email
        }
        
        # Personalize the content
        content = template.content
        content = content.replace('{{name}}', sample_contact['name'])
        content = content.replace('{{email}}', sample_contact['email'])
        
        # Create test tracking IDs (not recorded in database)
        test_job_id = 0
        test_contact_id = 0
        
        # Add tracking for preview purposes if enabled
        if template.has_open_tracking:
            content = add_open_tracking(content, test_job_id, test_contact_id)
        
        if template.has_click_tracking:
            content = add_click_tracking(content, test_job_id, test_contact_id)
            
        # Set the sender
        sender_email = smtp_config.from_email
        sender_name = smtp_config.from_name
        sender = f"{sender_name} <{sender_email}>" if sender_name else sender_email
        
        # Add test label to subject
        test_subject = f"[TEST] {template.subject}"
        
        # Create and send the message
        msg = Message(
            subject=test_subject,
            recipients=[recipient_email],
            html=content,
            sender=sender
        )
        
        mail.send(msg)
        
        return True, f"Test email sent successfully to {recipient_email}"
        
    except Exception as e:
        logging.error(f"Error sending test email: {str(e)}")
        logging.error(traceback.format_exc())
        return False, f"Error sending test email: {str(e)}"
