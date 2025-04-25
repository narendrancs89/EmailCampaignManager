import logging
from flask_mail import Mail, Message
from models import ScheduledJob, SMTPConfig, EmailSegment, EmailTemplate, Contact, JobLog
from app import db, mail
import time
from bs4 import BeautifulSoup
import uuid
import traceback

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
                
                # Add tracking if needed
                if template.type == 'open':
                    personalized_content = add_open_tracking(personalized_content, job.id, contact.id)
                
                if template.type == 'click':
                    personalized_content = add_click_tracking(personalized_content, job.id, contact.id)
                
                # Create the email message
                msg = Message(
                    subject=template.subject,
                    recipients=[contact.email],
                    html=personalized_content
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
    tracking_pixel = f'<img src="https://yourdomain.com/track/open/{job_id}/{contact_id}/{tracking_id}" width="1" height="1" alt="" />'
    
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
            tracking_id = str(uuid.uuid4())
            tracked_url = f"https://yourdomain.com/track/click/{job_id}/{contact_id}/{tracking_id}?url={original_url}"
            link['href'] = tracked_url
    
    return str(soup)
