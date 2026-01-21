#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run migrations (POC: creates tables in /tmp/db.sqlite3)
python3.9 manage.py migrate --noinput

# Create superuser for POC (will fail if already exists, that's OK)
python3.9 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else None" || true

# Collect static files
python3.9 manage.py collectstatic --noinput --clear
