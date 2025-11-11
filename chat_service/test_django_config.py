
#!/usr/bin/env python3
"""
Utility untuk testing konfigurasi Django chat service
Usage: python test_django_config.py
"""
import os
import sys
import django
from pathlib import Path

def test_django_config():
    """Test Django configuration and models"""
    print("[TEST] Testing Django configuration...")
    
    # Setup paths
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
    
    try:
        django.setup()
        print("[OK] Django setup successful")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            print(f"[OK] Database connection: {result}")
        
        # Test models import
        from chat.models import ChatRoom, ChatMessage, ChatSession
        print("[OK] Models imported successfully")
        
        # Test creating a room (will fail if tables don't exist)
        room_count = ChatRoom.objects.count()
        print(f"[OK] Current chat rooms: {room_count}")
        
        # Test Django admin
        from django.contrib.auth.models import User
        admin_count = User.objects.filter(is_superuser=True).count()
        print(f"[INFO] Django admin users: {admin_count}")
        
        print("[SUCCESS] All Django tests passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Django test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_django_config()
