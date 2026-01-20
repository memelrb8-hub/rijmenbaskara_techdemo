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

# Import WSGI application
from rijmenbaskara.wsgi import application

# Vercel entry point
app = application
