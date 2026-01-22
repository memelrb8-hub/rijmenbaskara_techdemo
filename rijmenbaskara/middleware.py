"""
Middleware to ensure database is initialized on Vercel.
POC: Now using /tmp/db.sqlite3 which persists within a function instance.
Still checks and creates admin if needed (cold starts may wipe /tmp).
"""
import os
from django.db import connection
from django.core.management import call_command


class VercelDatabaseMiddleware:
    """
    POC Middleware: Ensures database tables exist and admin user is created.
    With /tmp/db.sqlite3, this should only run once per function instance.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self._initialized = False
    
    def __call__(self, request):
        # Only check once per function instance
        if not self._initialized:
            self.ensure_database()
            self._initialized = True
        
        # POC: Auto-login all users as admin
        request.session['is_authenticated'] = True
        request.session['username'] = 'admin'
        
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
                print("POC: Creating database tables in /tmp/db.sqlite3...")
                # Create all tables
                call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
            
            # Always check if admin user exists and create if missing
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
            
            # Check if admin exists
            admin_exists = User.objects.filter(username=username).exists()
            
            if not admin_exists:
                print(f"POC: Creating superuser: {username}")
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                print(f"POC: Superuser '{username}' created with password '{password}'")
                
                # Verify it was created
                if User.objects.filter(username=username).exists():
                    admin_user = User.objects.get(username=username)
                    print(f"POC: Verified user '{username}' (ID: {admin_user.id}, staff: {admin_user.is_staff}, superuser: {admin_user.is_superuser})")
                else:
                    print(f"POC WARNING: Failed to create user '{username}'")
            else:
                print(f"POC: Admin user '{username}' already exists in /tmp/db.sqlite3")
            
        except Exception as e:
            # Log but don't crash
            print(f"POC: Database initialization error: {e}")
            import traceback
            traceback.print_exc()


