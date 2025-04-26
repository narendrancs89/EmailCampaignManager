from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta
import random
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
    
    # Calculate optimal send time if feature is enabled
    run_date = db_job.scheduled_time
    
    if db_job.use_optimal_time:
        run_date = calculate_optimal_send_time(db_job)
        
        # Update the job's actual scheduled time in the database and log the change
        with app.app_context():
            # Only update if it's different from the original time
            if run_date != db_job.scheduled_time:
                # Store the original time for reference
                original_time = db_job.scheduled_time
                
                # Update the scheduled time in the database
                db_job.actual_send_time = run_date  # Using a separate field to preserve the original time
                db.session.commit()
                
                # Log the rescheduling
                log_entry = JobLog(
                    job_id=db_job.id, 
                    level='info', 
                    message=f"Smart Scheduling: Job optimized from {original_time.strftime('%Y-%m-%d %H:%M')} to {run_date.strftime('%Y-%m-%d %H:%M')} for better engagement"
                )
                db.session.add(log_entry)
                db.session.commit()
    
    # Schedule the job
    scheduler.add_job(
        run_email_job,
        'date',
        args=[app, db_job.id],
        run_date=run_date,
        id=job_id,
        replace_existing=True
    )
    
    logging.info(f"Added job {job_id} to scheduler, will run at {run_date}")
    
def calculate_optimal_send_time(job):
    """
    Calculate the optimal send time based on the job settings.
    
    Args:
        job: The ScheduledJob instance
        
    Returns:
        datetime: The optimal send time
    """
    # Start with the original scheduled time
    original_time = job.scheduled_time
    
    # If no smart scheduling, just return the original time
    if not job.use_optimal_time:
        return original_time
    
    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = original_time.weekday()
    
    # Check day preference constraints
    if job.optimal_day_preference == 'weekday' and day_of_week >= 5:  # Weekend
        # Move to next Monday
        days_to_add = 7 - day_of_week
        original_time = original_time + timedelta(days=days_to_add)
    elif job.optimal_day_preference == 'weekend' and day_of_week < 5:  # Weekday
        # Move to next Saturday
        days_to_add = 5 - day_of_week
        original_time = original_time + timedelta(days=days_to_add)
    
    # Get the time window
    start_hour = job.optimal_time_window_start
    end_hour = job.optimal_time_window_end
    
    # Validate the time window (ensure it's at least 1 hour window)
    if start_hour is None or end_hour is None or start_hour >= end_hour:
        start_hour = 9  # Default to 9 AM
        end_hour = 17   # Default to 5 PM
    
    # Make sure the scheduled time is not earlier than the window start
    current_hour = original_time.hour
    
    if current_hour < start_hour:
        # Need to move to the start of the window
        time_delta = timedelta(hours=(start_hour - current_hour))
        adjusted_time = original_time + time_delta
    elif current_hour > end_hour:
        # Need to move to the next day's start window
        time_delta = timedelta(days=1, hours=(start_hour - current_hour))
        adjusted_time = original_time + time_delta
    else:
        # Already within window, keep the same time
        adjusted_time = original_time
    
    # Apply a small random offset within the window to avoid sending all emails at the same time
    hours_in_window = end_hour - max(current_hour, start_hour)
    if hours_in_window > 0:
        random_offset = random.randint(0, min(hours_in_window * 60, 120))  # Max 2 hours or window size
        adjusted_time = adjusted_time + timedelta(minutes=random_offset)
    
    return adjusted_time

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
