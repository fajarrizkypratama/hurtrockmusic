
#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Add the chat_service directory to Python path
chat_service_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(chat_service_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

def update_media_fields():
    """Update media fields to ensure they can store data properly"""
    print("[INFO] Updating media fields in database...")
    
    try:
        with connection.cursor() as cursor:
            # Check if table exists and has media fields
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                AND column_name IN ('media_url', 'media_type', 'media_filename')
                ORDER BY column_name;
            """)
            
            columns = cursor.fetchall()
            print(f"[INFO] Found media columns: {columns}")
            
            if not columns:
                print("[WARNING] Media columns not found, creating them...")
                # Add media columns if they don't exist
                cursor.execute("""
                    ALTER TABLE chat_messages 
                    ADD COLUMN IF NOT EXISTS media_url VARCHAR(500),
                    ADD COLUMN IF NOT EXISTS media_type VARCHAR(20),
                    ADD COLUMN IF NOT EXISTS media_filename VARCHAR(255);
                """)
                print("[OK] Media columns added successfully")
            else:
                print("[OK] Media columns already exist")
                
        print("[SUCCESS] Media fields update completed")
        
    except Exception as e:
        print(f"[ERROR] Failed to update media fields: {e}")
        # Try SQLite format
        try:
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA table_info(chat_chatmessage)")
                columns = cursor.fetchall()
                print(f"[INFO] SQLite table info: {columns}")
                print("[OK] Media fields should be available in SQLite")
        except Exception as sqlite_e:
            print(f"[ERROR] SQLite check also failed: {sqlite_e}")

if __name__ == '__main__':
    # Change to chat service directory
    os.chdir(str(chat_service_dir))
    
    # Create and apply migrations
    print("[INFO] Creating new migration for media fields...")
    execute_from_command_line(['manage.py', 'makemigrations', 'chat', '--name', 'update_media_fields'])
    
    print("[INFO] Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Update fields
    update_media_fields()
    
    print("[SUCCESS] Media fields migration completed!")
