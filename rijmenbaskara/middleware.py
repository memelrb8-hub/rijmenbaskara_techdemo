"""
Middleware to ensure database is initialized on Vercel.
This handles the in-memory database setup for each serverless function instance.
"""
import os
from django.core.management import call_command


_db_initialized = False


class VercelDatabaseMiddleware:
    """
    Middleware that ensures the in-memory database is initialized
    before processing any requests on Vercel.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.ensure_database()
    
    def __call__(self, request):
        self.ensure_database()
        return self.get_response(request)
    
    @classmethod
    def ensure_database(cls):
        """Initialize database tables and create superuser if needed."""
        global _db_initialized
        
        if _db_initialized:
            return
        
        if not os.environ.get('VERCEL'):
            _db_initialized = True
            return
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Check if tables exist by trying a simple query
            try:
                User.objects.exists()
                _db_initialized = True
                return
            except Exception:
                # Tables don't exist, need to create them
                pass
            
            # Run migrations to create tables
            call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
            
            # Create superuser
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
            
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
            
            _db_initialized = True
            
        except Exception as e:
            # Log error but don't crash the app
            print(f"Database initialization error: {e}")
            import traceback
            traceback.print_exc()
            _db_initialized = True  # Prevent infinite retry
