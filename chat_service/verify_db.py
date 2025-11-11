
#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
django.setup()

from chat.models import ChatRoom, ChatMessage, ChatSession
from django.db import connection

def verify_database():
    """Verify database setup and show table status"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("[OK] Database connection successful")
        
        # Check tables exist
        from django.db import connection
        table_names = connection.introspection.table_names()
        expected_tables = ['chat_rooms', 'chat_messages', 'chat_sessions']
        
        for table in expected_tables:
            if table in table_names:
                print(f"[OK] Table {table} exists")
            else:
                print(f"[ERROR] Table {table} missing")
        
        # Check model operations
        room_count = ChatRoom.objects.count()
        message_count = ChatMessage.objects.count()
        session_count = ChatSession.objects.count()
        
        print(f"📊 Current data:")
        print(f"   - Rooms: {room_count}")
        print(f"   - Messages: {message_count}")
        print(f"   - Sessions: {session_count}")
        
        # Test creating a sample room
        test_room, created = ChatRoom.objects.get_or_create(
            name='test_verification',
            defaults={
                'buyer_id': 999,
                'buyer_name': 'Test User',
                'buyer_email': 'test@example.com'
            }
        )
        
        if created:
            print("[OK] Test room created successfully")
            test_room.delete()
            print("[OK] Test room deleted successfully")
        else:
            print("ℹ️  Test room already exists")
        
        print("\n[SUCCESS] Database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_database()
