import os
import json
import requests
from flask import current_app, url_for
import logging

# Brevo API configuration
BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'
BREVO_API_KEY = os.environ.get('BREVO_API_KEY')

def send_email_with_brevo(to_email, subject, html_content, text_content=None, from_email=None, from_name=None):
    """
    Send email using Brevo API
    """
    if not BREVO_API_KEY:
        logging.error("BREVO_API_KEY is not set")
        return False
    
    # Use default sender if not provided
    if not from_email:
        from_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
        if isinstance(from_email, tuple):
            from_email, from_name = from_email
    
    # Prepare request payload
    payload = {
        'sender': {
            'email': from_email
        },
        'to': [{'email': to_email}],
        'subject': subject,
        'htmlContent': html_content
    }
    
    # Add sender name if provided
    if from_name:
        payload['sender']['name'] = from_name
    
    # Add text content if provided
    if text_content:
        payload['textContent'] = text_content
    
    # Make API request
    headers = {
        'accept': 'application/json',
        'api-key': BREVO_API_KEY,
        'content-type': 'application/json'
    }
    
    try:
        response = requests.post(BREVO_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code >= 200 and response.status_code < 300:
            logging.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logging.error(f"Failed to send email. Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Exception when sending email: {str(e)}")
        return False

def send_verification_email(email, token):
    """Send an email verification link to the user"""
    try:
        verify_url = url_for('verify_email', token=token, _external=True)
        html_content = f'''
        <p>To verify your email address, click the button below:</p>
        <p><a href="{verify_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
        <p>Or visit this link: <a href="{verify_url}">{verify_url}</a></p>
        <p>If you did not make this request, simply ignore this email.</p>
        '''
        
        text_content = f'''To verify your email address, visit the following link:
{verify_url}

If you did not make this request, simply ignore this email.
'''
        
        return send_email_with_brevo(
            to_email=email,
            subject='Verify Your Email Address',
            html_content=html_content,
            text_content=text_content
        )
    except Exception as e:
        logging.error(f"Error sending verification email: {str(e)}")
        return False
        
def send_password_reset_email(email, token):
    """Send a password reset link to the user"""
    try:
        reset_url = url_for('reset_password', token=token, _external=True)
        html_content = f'''
        <p>To reset your password, click the button below:</p>
        <p><a href="{reset_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>Or visit this link: <a href="{reset_url}">{reset_url}</a></p>
        <p>If you did not make this request, simply ignore this email.</p>
        <p>This link will expire in 1 hour.</p>
        '''
        
        text_content = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email.
This link will expire in 1 hour.
'''
        
        return send_email_with_brevo(
            to_email=email,
            subject='Password Reset Request',
            html_content=html_content,
            text_content=text_content
        )
    except Exception as e:
        logging.error(f"Error sending password reset email: {str(e)}")
        return False
        
def send_approval_notification(email, username):
    """Send an approval notification to the user"""
    try:
        login_url = url_for('login', _external=True)
        html_content = f'''
        <p>Congratulations! Your account <strong>{username}</strong> has been approved.</p>
        <p>You can now <a href="{login_url}">log in to your account</a>.</p>
        '''
        
        text_content = f'''Your account {username} has been approved!
You can now log in at: {login_url}
'''
        
        return send_email_with_brevo(
            to_email=email,
            subject='Account Approved',
            html_content=html_content,
            text_content=text_content
        )
    except Exception as e:
        logging.error(f"Error sending approval notification: {str(e)}")
        return False
        
def send_rejection_notification(email, username, reason):
    """Send a rejection notification to the user"""
    try:
        register_url = url_for('register', _external=True)
        html_content = f'''
        <p>Unfortunately, your account registration for <strong>{username}</strong> was not approved.</p>
        <p><strong>Reason:</strong> {reason}</p>
        <p>You may <a href="{register_url}">register again</a> if you wish.</p>
        '''
        
        text_content = f'''Unfortunately, your account registration for {username} was not approved.
Reason: {reason}

You may register again at: {register_url}
'''
        
        return send_email_with_brevo(
            to_email=email,
            subject='Account Registration Status',
            html_content=html_content,
            text_content=text_content
        )
    except Exception as e:
        logging.error(f"Error sending rejection notification: {str(e)}")
        return False