from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta
from models import ScheduledJob, JobLog
from email_service import send_campaign_emails
from app import db
import logging

scheduler = None

def init_scheduler(app):
    """Initialize the scheduler with the Flask app context"""
    global scheduler
    
    if scheduler:
        scheduler.shutdown()
    
    # Configure job stores and executors
    jobstores = {
        'default': MemoryJobStore()
    }
    executors = {
        'default': ThreadPoolExecutor(10)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    
    # Create scheduler
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
    
    # Start the scheduler
    scheduler.start()
    
    # Load existing jobs from database
    with app.app_context():
        load_jobs_from_db(app)
    
    # Add a job to check for new scheduled jobs every minute
    scheduler.add_job(
        check_for_new_jobs,
        'interval',
        args=[app],
        minutes=1,
        id='job_checker',
        replace_existing=True
    )
    
    logging.info("Scheduler initialized")
    
    return scheduler

def load_jobs_from_db(app):
    """Load existing jobs from database that are scheduled but not yet run"""
    with app.app_context():
        # Get jobs that are scheduled to run in the future
        scheduled_jobs = ScheduledJob.query.filter(
            ScheduledJob.status == 'scheduled',
            ScheduledJob.scheduled_time > datetime.utcnow()
        ).all()
        
        for job in scheduled_jobs:
            add_job_to_scheduler(app, job)

def check_for_new_jobs(app):
    """Check for newly added jobs in the database"""
    with app.app_context():
        # Get jobs that are scheduled to run in the future and not in the scheduler
        scheduled_jobs = ScheduledJob.query.filter(
            ScheduledJob.status == 'scheduled',
            ScheduledJob.scheduled_time > datetime.utcnow()
        ).all()
        
        for job in scheduled_jobs:
            # Check if this job is already in the scheduler
            try:
                if not scheduler.get_job(f'email_job_{job.id}'):
                    add_job_to_scheduler(app, job)
            except:
                # If job doesn't exist, add it
                add_job_to_scheduler(app, job)

def add_job_to_scheduler(app, db_job):
    """Add a job to the scheduler"""
    job_id = f'email_job_{db_job.id}'
    
    # Schedule the job
    scheduler.add_job(
        run_email_job,
        'date',
        args=[app, db_job.id],
        run_date=db_job.scheduled_time,
        id=job_id,
        replace_existing=True
    )
    
    logging.info(f"Added job {job_id} to scheduler, will run at {db_job.scheduled_time}")

def run_email_job(app, job_id):
    """Execute the email job"""
    with app.app_context():
        job = ScheduledJob.query.get(job_id)
        
        if not job or job.status != 'scheduled':
            logging.warning(f"Job {job_id} not found or not in scheduled state")
            return
        
        # Update job status to running
        job.status = 'running'
        log_entry = JobLog(job_id=job.id, message=f"Job started execution", level='info')
        db.session.add(log_entry)
        db.session.commit()
        
        try:
            # Send the emails
            success, total, sent, failed = send_campaign_emails(app, job)
            
            # Update job statistics
            job.sent_emails = sent
            job.failed_emails = failed
            
            # Update job status
            if success:
                job.status = 'completed'
                log_message = f"Job completed successfully. Sent: {sent}, Failed: {failed}"
                log_level = 'info'
            else:
                job.status = 'failed'
                log_message = f"Job execution failed. Sent: {sent}, Failed: {failed}"
                log_level = 'error'
            
            log_entry = JobLog(job_id=job.id, message=log_message, level=log_level)
            db.session.add(log_entry)
            db.session.commit()
            
            logging.info(f"Job {job_id} executed. Status: {job.status}")
            
        except Exception as e:
            # Handle any exceptions
            job.status = 'failed'
            log_entry = JobLog(job_id=job.id, message=f"Job failed with error: {str(e)}", level='error')
            db.session.add(log_entry)
            db.session.commit()
            
            logging.error(f"Error executing job {job_id}: {str(e)}")
