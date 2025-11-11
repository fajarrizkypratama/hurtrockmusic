
#!/usr/bin/env python3
"""
Reset and test script for Django chat service
"""
import os
import sys
import django
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from chat.models import ChatRoom, ChatMessage, ChatSession

def reset_database():
    """Reset chat database"""
    print("🔄 Resetting chat database...")
    
    try:
        # Delete all chat data
        ChatMessage.objects.all().delete()
        ChatSession.objects.all().delete()
        ChatRoom.objects.all().delete()
        print("[OK] Chat data cleared")
        
        # Test basic functionality
        test_room = ChatRoom.objects.create(
            name='test_buyer_1',
            buyer_id=1,
            buyer_name='Test Buyer',
            buyer_email='buyer@test.com'
        )
        
        test_message = ChatMessage.objects.create(
            room=test_room,
            user_id=1,
            user_name='Test Buyer',
            user_email='buyer@test.com',
            message='Hello, this is a test message!',
            sender_type='buyer'
        )
        
        test_session = ChatSession.objects.create(
            room=test_room,
            user_id=1,
            user_name='Test Buyer',
            user_email='buyer@test.com',
            user_role='buyer'
        )
        
        print("[OK] Test data created successfully")
        print(f"   - Room: {test_room.name}")
        print(f"   - Message: {test_message.message}")
        print(f"   - Session: {test_session.user_name}")
        
        # Verify relationships
        assert test_room.messages.count() == 1
        assert test_room.sessions.count() == 1
        print("[OK] Model relationships working correctly")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during reset: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            print(f"[OK] Database connected: {result[0] if result else 'Unknown'}")
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("[START] Chat Service Reset & Test Script")
    print("=" * 50)
    
    # Test database connection
    if not test_database_connection():
        sys.exit(1)
    
    # Reset and test
    if reset_database():
        print("\n[OK] Chat service is ready to use!")
        print("You can now start the server with: python manage.py runserver 0.0.0.0:8000")
    else:
        print("\n[ERROR] Chat service setup failed!")
        sys.exit(1)
