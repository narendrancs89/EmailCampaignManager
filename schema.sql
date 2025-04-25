-- Email Marketing Platform Database Schema

-- User table
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    verification_token_expires TIMESTAMP,
    reset_password_token VARCHAR(100),
    reset_token_expires TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
    permissions TEXT DEFAULT '{}'
);

-- Email Segment table
CREATE TABLE IF NOT EXISTS "email_segment" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER NOT NULL REFERENCES "user"(id)
);

-- Contact table
CREATE TABLE IF NOT EXISTS "contact" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    name VARCHAR(120),
    segment_id INTEGER NOT NULL REFERENCES "email_segment"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Email Template table
CREATE TABLE IF NOT EXISTS "email_template" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(100) NOT NULL,
    has_click_tracking BOOLEAN DEFAULT FALSE,
    has_open_tracking BOOLEAN DEFAULT FALSE,
    has_optout BOOLEAN DEFAULT FALSE,
    click_tracking_url VARCHAR(500),
    open_tracking_url VARCHAR(500),
    optout_url VARCHAR(500),
    tracking_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    is_draft BOOLEAN DEFAULT FALSE,
    parent_id INTEGER REFERENCES "email_template"(id),
    version INTEGER DEFAULT 1
);

-- SMTP Configuration table
CREATE TABLE IF NOT EXISTS "smtp_config" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    host VARCHAR(100) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(256) NOT NULL,
    use_tls BOOLEAN DEFAULT TRUE,
    use_ssl BOOLEAN DEFAULT FALSE,
    from_email VARCHAR(120) NOT NULL,
    from_name VARCHAR(120),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER NOT NULL REFERENCES "user"(id)
);

-- Scheduled Job table
CREATE TABLE IF NOT EXISTS "scheduled_job" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    template_id INTEGER NOT NULL REFERENCES "email_template"(id),
    segment_id INTEGER NOT NULL REFERENCES "email_segment"(id),
    smtp_config_id INTEGER NOT NULL REFERENCES "smtp_config"(id),
    from_email VARCHAR(120),
    from_name VARCHAR(120),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    current_batch INTEGER DEFAULT 0,
    batch_size INTEGER DEFAULT 100,
    total_emails INTEGER DEFAULT 0,
    sent_emails INTEGER DEFAULT 0,
    failed_emails INTEGER DEFAULT 0,
    opened_emails INTEGER DEFAULT 0,
    clicked_emails INTEGER DEFAULT 0,
    sending_started_at TIMESTAMP,
    sending_completed_at TIMESTAMP,
    avg_sending_rate FLOAT DEFAULT 0.0
);

-- Job Log table
CREATE TABLE IF NOT EXISTS "job_log" (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES "scheduled_job"(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT NOW(),
    message TEXT NOT NULL,
    level VARCHAR(20) DEFAULT 'info'
);

-- Email Open Tracking table
CREATE TABLE IF NOT EXISTS "email_open" (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES "scheduled_job"(id) ON DELETE CASCADE,
    contact_id INTEGER NOT NULL REFERENCES "contact"(id) ON DELETE CASCADE,
    tracking_id VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

-- Email Click Tracking table
CREATE TABLE IF NOT EXISTS "email_click" (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES "scheduled_job"(id) ON DELETE CASCADE,
    contact_id INTEGER NOT NULL REFERENCES "contact"(id) ON DELETE CASCADE,
    tracking_id VARCHAR(64) NOT NULL,
    url TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

-- User Session table
CREATE TABLE IF NOT EXISTS "user_session" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    login_time TIMESTAMP DEFAULT NOW(),
    logout_time TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

-- Admin Email List table
CREATE TABLE IF NOT EXISTS "admin_email_list" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER NOT NULL REFERENCES "user"(id)
);

-- Admin Email Contact table
CREATE TABLE IF NOT EXISTS "admin_email_contact" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    name VARCHAR(120),
    company VARCHAR(120),
    phone VARCHAR(50),
    additional_data TEXT,
    list_id INTEGER NOT NULL REFERENCES "admin_email_list"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Registration Request table
CREATE TABLE IF NOT EXISTS "user_registration_request" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    verification_token VARCHAR(100) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    request_date TIMESTAMP DEFAULT NOW(),
    approved BOOLEAN DEFAULT FALSE,
    approved_by INTEGER REFERENCES "user"(id),
    approval_date TIMESTAMP,
    rejected BOOLEAN DEFAULT FALSE,
    rejection_reason TEXT
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_contact_segment_id ON "contact" (segment_id);
CREATE INDEX IF NOT EXISTS idx_template_user_id ON "email_template" (user_id);
CREATE INDEX IF NOT EXISTS idx_job_user_id ON "scheduled_job" (user_id);
CREATE INDEX IF NOT EXISTS idx_job_status ON "scheduled_job" (status);
CREATE INDEX IF NOT EXISTS idx_job_scheduled_time ON "scheduled_job" (scheduled_time);
CREATE INDEX IF NOT EXISTS idx_email_open_job_id ON "email_open" (job_id);
CREATE INDEX IF NOT EXISTS idx_email_click_job_id ON "email_click" (job_id);
CREATE INDEX IF NOT EXISTS idx_job_log_job_id ON "job_log" (job_id);