
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
django.setup()

from chat.models import ChatRoom, ChatMessage, ChatSession
from django.db import connection
from django.utils import timezone

def test_database():
    """Test database functionality"""
    try:
        print("🔍 Testing database functionality...")
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("[OK] Database connection successful")
        
        # Test model operations
        print("\n📝 Testing model operations...")
        
        # Create test room
        room = ChatRoom.objects.create(
            name='test_room_123',
            buyer_id=1,
            buyer_name='Test User',
            buyer_email='test@example.com'
        )
        print(f"[OK] Created room: {room.name}")
        
        # Create test message
        message = ChatMessage.objects.create(
            room=room,
            user_id=1,
            user_name='Test User',
            user_email='test@example.com',
            message='Test message',
            sender_type='buyer'
        )
        print(f"[OK] Created message: {message.id}")
        
        # Create test session
        session = ChatSession.objects.create(
            room=room,
            user_id=1,
            user_name='Test User',
            user_email='test@example.com',
            user_role='buyer'
        )
        print(f"[OK] Created session: {session.id}")
        
        # Test queries
        room_count = ChatRoom.objects.count()
        message_count = ChatMessage.objects.count()
        session_count = ChatSession.objects.count()
        
        print(f"\n📊 Current counts:")
        print(f"   - Rooms: {room_count}")
        print(f"   - Messages: {message_count}")
        print(f"   - Sessions: {session_count}")
        
        # Test relationships
        room_messages = room.messages.count()
        room_sessions = room.sessions.count()
        print(f"   - Room {room.name} has {room_messages} messages and {room_sessions} sessions")
        
        # Clean up test data
        ChatSession.objects.filter(room=room).delete()
        ChatMessage.objects.filter(room=room).delete()
        ChatRoom.objects.filter(name='test_room_123').delete()
        print("🧹 Cleaned up test data")
        
        print("\n[SUCCESS] Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database()
