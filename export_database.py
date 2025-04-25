import os
import sys
import subprocess
import datetime

def export_database():
    """
    Export the PostgreSQL database to a SQL file.
    This creates both a schema-only file and a full dump with data.
    """
    # Get database connection details from environment variables
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL environment variable not found.")
        return False
    
    # Extract connection details from the URL
    # Format expected: postgresql://username:password@host:port/dbname
    # Skip the 'postgresql://' part
    conn_string = db_url.split('://')[1]
    
    # Extract username, password, host, port, and dbname
    if '@' in conn_string:
        auth, conn = conn_string.split('@')
        username, password = auth.split(':')
    else:
        username = ''
        password = ''
        conn = conn_string
    
    if '/' in conn:
        hostport, dbname_with_params = conn.split('/')
    else:
        hostport = conn
        dbname_with_params = ''
    
    # Handle SSL mode and other parameters
    if '?' in dbname_with_params:
        dbname = dbname_with_params.split('?')[0]
    else:
        dbname = dbname_with_params
    
    if ':' in hostport:
        host, port = hostport.split(':')
    else:
        host = hostport
        port = '5432'  # Default PostgreSQL port
    
    # Create export directory if it doesn't exist
    export_dir = 'database_exports'
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Generate filenames with timestamps
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    schema_filename = f"{export_dir}/schema_{timestamp}.sql"
    data_filename = f"{export_dir}/full_dump_{timestamp}.sql"
    
    # Set environment variables for pg_dump (so we don't need to pass password on command line)
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    # Export schema only
    try:
        schema_cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', username,
            '-d', dbname,
            '--schema-only',
            '--no-owner',        # Remove ownership to make it portable
            '--no-privileges',   # Skip privilege assignments
            '--clean',           # Include drop statements
            '--if-exists',       # Add IF EXISTS to drop statements
            '-f', schema_filename
        ]
        # For Neon.tech and other cloud PostgreSQL services, add SSL mode
        env['PGSSLMODE'] = 'require'
        
        subprocess.run(schema_cmd, env=env, check=True)
        print(f"Schema exported successfully to {schema_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Error exporting schema: {e}")
        return False
    
    # Export full dump (schema + data)
    try:
        data_cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', username,
            '-d', dbname,
            '--no-owner',        # Remove ownership to make it portable
            '--no-privileges',   # Skip privilege assignments 
            '-f', data_filename
        ]
        subprocess.run(data_cmd, env=env, check=True)
        print(f"Full database dump exported successfully to {data_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Error exporting full dump: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting database export...")
    if export_database():
        print("Database export completed successfully!")
    else:
        print("Database export failed.")
        sys.exit(1)