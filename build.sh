#!/usr/bin/env bash
# build.sh - Render build script

set -o errexit  # exit on error

echo "Installing dependencies..."
pip install -r render_requirements.txt

echo "DATABASE_URL is: $DATABASE_URL"

# Wait for database to be ready
echo "Waiting for database to be ready..."
python -c "
import os
import time
import psycopg2
from urllib.parse import urlparse

if os.environ.get('DATABASE_URL'):
    url = urlparse(os.environ['DATABASE_URL'])
    for i in range(30):
        try:
            conn = psycopg2.connect(
                host=url.hostname,
                port=url.port,
                user=url.username,
                password=url.password,
                database=url.path[1:]
            )
            conn.close()
            print('Database connection successful')
            break
        except Exception as e:
            print(f'Waiting for database... {i+1}/30')
            time.sleep(2)
    else:
        print('Database connection failed after 30 attempts')
        exit(1)
"

echo "Running production database initialization..."
python deployment_init.py

echo "Verifying deployment readiness..."
python final_deployment_test.py