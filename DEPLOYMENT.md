# Email Marketing Platform - Deployment Guide

## Render Deployment Instructions

### Prerequisites
1. GitHub repository with your code
2. Render account
3. PostgreSQL database on Render

### Step 1: Database Setup
1. Create a PostgreSQL database on Render
2. Note the database connection details

### Step 2: Environment Variables
Set these environment variables in Render:

```
DATABASE_URL=<your_postgresql_connection_string>
SESSION_SECRET=<generate_random_secret>
BREVO_API_KEY=<your_brevo_api_key> (optional)
SENDGRID_API_KEY=<your_sendgrid_api_key> (optional)
```

### Step 3: Deployment Configuration
The project includes:
- `render.yaml` - Service configuration
- `render_requirements.txt` - Python dependencies
- `build.sh` - Build script that handles database initialization

### Step 4: Deploy
1. Connect your GitHub repository to Render
2. Select "Web Service"
3. Choose your repository
4. Render will automatically detect the `render.yaml` configuration

### Step 5: Post-Deployment
After successful deployment:
1. The database tables will be automatically created
2. Default admin user will be created:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `Admin123!`

### Troubleshooting Common Issues

#### SQLAlchemy Query Issues
If you encounter PostgreSQL parameter binding errors:
- The codebase has been updated to use proper SQLAlchemy query syntax
- Queries are separated into individual filter calls for better PostgreSQL compatibility

#### Database Connection Issues
- Ensure DATABASE_URL is correctly set
- Check that the PostgreSQL database is accessible
- Verify connection pooling settings in the configuration

#### Build Failures
- Check that all dependencies in `render_requirements.txt` are compatible
- Ensure the build script has proper permissions

### Security Notes
- Change the default admin password immediately after first login
- Set strong SESSION_SECRET in production
- Use environment variables for all sensitive configuration

### Performance Optimization
- Database connection pooling is configured for production
- SQLAlchemy echo is disabled in production
- Proper logging levels are set for production environment

## Local Development
For local development:
1. Install dependencies: `pip install -r render_requirements.txt`
2. Set up local PostgreSQL or use SQLite
3. Run database initialization: `python init_db.py`
4. Start the application: `gunicorn --bind 0.0.0.0:5000 main:app`