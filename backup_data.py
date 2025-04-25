import os
import sys
import json
import datetime
from app import app, db
from models import User, EmailSegment, Contact, EmailTemplate, SMTPConfig, ScheduledJob

def backup_data():
    """
    Export essential data from the database to JSON files
    """
    # Create backup directory
    backup_dir = 'database_backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        with app.app_context():
            # Back up Users (excluding sensitive fields)
            users = User.query.all()
            user_data = []
            for user in users:
                # Skip password hash and tokens for security
                user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'created_at': str(user.created_at),
                    'last_login': str(user.last_login) if user.last_login else None,
                    'email_verified': user.email_verified,
                    'is_active': user.is_active,
                    'is_admin': user.is_admin,
                    'permissions': user.permissions
                })
            
            with open(f'{backup_dir}/users_{timestamp}.json', 'w') as f:
                json.dump(user_data, f, indent=2)
                
            # Back up Segments
            segments = EmailSegment.query.all()
            segment_data = []
            for segment in segments:
                segment_data.append({
                    'id': segment.id,
                    'name': segment.name,
                    'description': segment.description,
                    'created_at': str(segment.created_at),
                    'updated_at': str(segment.updated_at),
                    'user_id': segment.user_id
                })
                
            with open(f'{backup_dir}/segments_{timestamp}.json', 'w') as f:
                json.dump(segment_data, f, indent=2)
                
            # Back up Contacts
            contacts = Contact.query.all()
            contact_data = []
            for contact in contacts:
                contact_data.append({
                    'id': contact.id,
                    'email': contact.email,
                    'name': contact.name,
                    'segment_id': contact.segment_id,
                    'created_at': str(contact.created_at)
                })
                
            with open(f'{backup_dir}/contacts_{timestamp}.json', 'w') as f:
                json.dump(contact_data, f, indent=2)
                
            # Back up Templates
            templates = EmailTemplate.query.all()
            template_data = []
            for template in templates:
                template_data.append({
                    'id': template.id,
                    'name': template.name,
                    'subject': template.subject,
                    'content': template.content,
                    'type': template.type,
                    'has_click_tracking': template.has_click_tracking,
                    'has_open_tracking': template.has_open_tracking,
                    'has_optout': template.has_optout,
                    'click_tracking_url': template.click_tracking_url,
                    'open_tracking_url': template.open_tracking_url,
                    'optout_url': template.optout_url,
                    'tracking_image_url': template.tracking_image_url,
                    'created_at': str(template.created_at),
                    'updated_at': str(template.updated_at),
                    'user_id': template.user_id,
                    'is_draft': template.is_draft,
                    'parent_id': template.parent_id,
                    'version': template.version
                })
                
            with open(f'{backup_dir}/templates_{timestamp}.json', 'w') as f:
                json.dump(template_data, f, indent=2)
                
            # Back up SMTP Configs (excluding sensitive fields)
            smtp_configs = SMTPConfig.query.all()
            smtp_data = []
            for config in smtp_configs:
                # Skip password for security
                smtp_data.append({
                    'id': config.id,
                    'name': config.name,
                    'host': config.host,
                    'port': config.port,
                    'username': config.username,
                    'use_tls': config.use_tls,
                    'use_ssl': config.use_ssl,
                    'from_email': config.from_email,
                    'from_name': config.from_name,
                    'created_at': str(config.created_at),
                    'updated_at': str(config.updated_at),
                    'user_id': config.user_id
                })
                
            with open(f'{backup_dir}/smtp_configs_{timestamp}.json', 'w') as f:
                json.dump(smtp_data, f, indent=2)
                
            # Back up Jobs
            jobs = ScheduledJob.query.all()
            job_data = []
            for job in jobs:
                job_data.append({
                    'id': job.id,
                    'name': job.name,
                    'scheduled_time': str(job.scheduled_time),
                    'status': job.status,
                    'created_at': str(job.created_at),
                    'updated_at': str(job.updated_at),
                    'user_id': job.user_id,
                    'template_id': job.template_id,
                    'segment_id': job.segment_id,
                    'smtp_config_id': job.smtp_config_id,
                    'from_email': job.from_email,
                    'from_name': job.from_name,
                    'started_at': str(job.started_at) if job.started_at else None,
                    'completed_at': str(job.completed_at) if job.completed_at else None,
                    'current_batch': job.current_batch,
                    'batch_size': job.batch_size,
                    'total_emails': job.total_emails,
                    'sent_emails': job.sent_emails,
                    'failed_emails': job.failed_emails,
                    'opened_emails': job.opened_emails,
                    'clicked_emails': job.clicked_emails
                })
                
            with open(f'{backup_dir}/jobs_{timestamp}.json', 'w') as f:
                json.dump(job_data, f, indent=2)
                
            print(f"Backed up data to {backup_dir} directory with timestamp {timestamp}")
            return True
    
    except Exception as e:
        print(f"Error backing up data: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting database backup...")
    if backup_data():
        print("Database backup completed successfully!")
    else:
        print("Database backup failed.")
        sys.exit(1)