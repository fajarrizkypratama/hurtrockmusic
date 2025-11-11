
#!/usr/bin/env python
import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line
import sys
from pathlib import Path

def reset_migrations():
    """Reset Django migrations"""
    # Setup Django
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
    django.setup()
    
    from django.db import connection
    from chat.models import ChatRoom, ChatMessage, ChatSession
    
    try:
        print("🔄 Resetting Django migrations...")
        
        # Drop all tables
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS chat_messages CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS chat_sessions CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS chat_rooms CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS django_migrations CASCADE;")
            print("[OK] Dropped existing tables")
        
        # Remove migration files (except __init__.py)
        migrations_dir = Path(__file__).parent / 'chat' / 'migrations'
        for file in migrations_dir.glob('*.py'):
            if file.name != '__init__.py':
                file.unlink()
                print(f"🗑️  Removed {file.name}")
        
        # Create fresh migrations
        os.chdir(current_dir)
        execute_from_command_line(['manage.py', 'makemigrations', 'chat'])
        print("[OK] Created new migrations")
        
        # Apply migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("[OK] Applied migrations successfully")
        
        # Verify tables
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'chat_%'
            """)
            tables = cursor.fetchall()
            print(f"📊 Created tables: {[table[0] for table in tables]}")
        
        print("[SUCCESS] Migration reset completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration reset failed: {e}")
        return False

if __name__ == "__main__":
    reset_migrations()
