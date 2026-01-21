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

# Initialize database for Vercel (must happen before importing application)
_db_initialized = False

def ensure_db_initialized():
    """Ensure database is initialized once per function instance."""
    global _db_initialized
    
    if _db_initialized:
        return
    
    if os.environ.get('VERCEL'):
        from django.core.management import call_command
        from django.db import connection
        
        try:
            # Run migrations to create tables
            call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
            
            # Create superuser
            call_command('create_vercel_superuser', verbosity=0)
            
            _db_initialized = True
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Try to continue anyway
            _db_initialized = True

# Initialize on module load
ensure_db_initialized()

# Import WSGI application
from rijmenbaskara.wsgi import application

# Vercel entry point with middleware to ensure DB is ready
class VercelDBMiddleware:
    """Middleware to ensure database is initialized before handling requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        ensure_db_initialized()
    
    def __call__(self, request):
        ensure_db_initialized()
        return self.get_response(request)

# Wrap application with our middleware
def app(environ, start_response):
    ensure_db_initialized()
    return application(environ, start_response)
