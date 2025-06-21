#!/usr/bin/env bash
# build.sh - Render build script

set -o errexit  # exit on error

pip install -r render_requirements.txt

# Run database initialization
python init_db.py