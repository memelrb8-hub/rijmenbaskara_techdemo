import os
import sys
from pathlib import Path

# Add the project directory to the sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rijmenbaskara.settings')

# Import Django
import django
django.setup()

# Initialize database and create superuser for Vercel
if os.environ.get('VERCEL'):
    from django.core.management import call_command
    
    # Run migrations (creates tables in-memory)
    call_command('migrate', '--run-syncdb', verbosity=0)
    
    # Create superuser
    call_command('create_vercel_superuser', verbosity=0)

# Import WSGI application
from rijmenbaskara.wsgi import application

# Vercel entry point
app = application
