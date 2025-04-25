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

### Database Backup and Restoration

#### Backing Up Your Database

To create a database backup:

```
python backup_data.py
```

This will create a set of JSON files in the `database_backups` directory with the current timestamp.

#### Restoring Your Database

To restore the database from the most recent backup:

```
python restore_data.py
```

To restore from a specific backup, provide the timestamp:

```
python restore_data.py 20250425_091409
```

**Important Notes on Restoration:**
- All user passwords will be reset to a default value (`ChangeMe123!_username`)
- SMTP server passwords will need to be manually updated after restoration
- Relationships between tables will be preserved

## Default Credentials

- Admin User:
  - Username: admin
  - Password: Admin123!

- Test User:
  - Username: testuser
  - Password: Test123!

## Pushing to GitHub

You can easily push your project to GitHub using the provided initialization script:

```bash
./init_git.sh https://github.com/yourusername/email-marketing-platform.git
```

The script will:
1. Create a database backup
2. Initialize a Git repository
3. Set up your Git user information
4. Add all files and make an initial commit
5. Push to the GitHub repository you specified

You will need to:
- Create an empty GitHub repository first
- Have Git installed
- Provide your GitHub credentials when prompted

## Security Notes

- Change default credentials immediately after setup
- Store API keys securely and never commit them to version control
- Enable HTTPS for production deployments
- All sensitive information (API keys, passwords) is excluded from Git commits by the .gitignore file

## License

[Your chosen license]