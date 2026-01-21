"""
Middleware to ensure database is initialized on Vercel.
This handles the in-memory database setup for each serverless function instance.
"""
import os
from django.db import connection
from django.core.management import call_command


class VercelDatabaseMiddleware:
    """
    Middleware that ensures the in-memory database is initialized
    before processing any requests on Vercel.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Ensure database is initialized on every request
        self.ensure_database()
        return self.get_response(request)
    
    @staticmethod
    def ensure_database():
        """Initialize database tables and create superuser if needed."""
        
        # Only run on Vercel
        if not os.environ.get('VERCEL'):
            return
        
        try:
            from django.contrib.auth import get_user_model
            from django.db import connection
            from django.core.management import call_command
            
            User = get_user_model()
            
            # Check if auth_user table exists
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'"
                )
                table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                # Create all tables
                call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
                
                # Create superuser
                username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
                email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
                password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
                
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
            
        except Exception as e:
            # Log but don't crash
            print(f"Database initialization error: {e}")
            import traceback
            traceback.print_exc()

