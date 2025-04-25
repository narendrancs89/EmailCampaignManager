# Email Marketing Campaign Platform

A comprehensive Flask-based email campaign management platform that enables users to create, design, and optimize email marketing campaigns with advanced features and user-friendly tools.

## Features

- User authentication system with email verification and admin approval
- HTML email template creation and management
- Email segment management for targeted campaigns
- Campaign scheduling and monitoring
- Custom sender information for each campaign
- Comprehensive email tracking (opens, clicks)
- Analytics dashboard
- SMTP configuration
- Admin user management

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database
- SMTP server for sending emails (or an email service like Brevo/SendGrid)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/email-marketing-platform.git
   cd email-marketing-platform
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@hostname:port/database_name
   FLASK_SECRET_KEY=your_secret_key
   BREVO_API_KEY=your_brevo_api_key  # If using Brevo for verification emails
   ```

4. Initialize the database:
   ```
   python create_admin_user.py
   ```

5. Run the application:
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

### Database Migration/Restoration

To restore the database from a SQL dump:

```
psql -U username -d database_name -f database_exports/schema_YYYYMMDD_HHMMSS.sql
psql -U username -d database_name -f database_exports/full_dump_YYYYMMDD_HHMMSS.sql
```

## Default Credentials

- Admin User:
  - Username: admin
  - Password: Admin123!

- Test User:
  - Username: testuser
  - Password: Test123!

## Security Notes

- Change default credentials immediately after setup
- Store API keys securely and never commit them to version control
- Enable HTTPS for production deployments

## License

[Your chosen license]