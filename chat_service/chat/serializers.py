from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'room', 'user_id', 'user_name', 'user_email', 
            'message', 'sender_type', 'product_id', 
            'media_url', 'media_type', 'media_filename',
            'is_read', 'is_deleted', 'created_at', 'updated_at',
            'formatted_created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'formatted_created_at']

    def to_representation(self, instance):
        """Custom representation to include media_data for frontend compatibility"""
        data = super().to_representation(instance)

        # Add media_data object for frontend compatibility
        if instance.media_url and instance.media_type:
            data['media_data'] = {
                'media_url': instance.media_url,
                'media_type': instance.media_type,
                'media_filename': instance.media_filename,
                'filename': instance.media_filename  # Alias for compatibility
            }
            # Also ensure direct fields are present
            data['media_url'] = instance.media_url
            data['media_type'] = instance.media_type
            data['media_filename'] = instance.media_filename

        # Ensure timestamp is properly formatted
        if instance.created_at:
            data['timestamp'] = instance.created_at.isoformat()

        return data


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms"""
    message_count = serializers.ReadOnlyField()
    last_message = ChatMessageSerializer(read_only=True)
    unread_messages_count = serializers.ReadOnlyField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'buyer_id', 'buyer_name', 'buyer_email',
            'created_at', 'is_active', 'message_count', 'last_message',
            'unread_messages_count'
        ]
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions"""
    duration = serializers.ReadOnlyField()

    class Meta:
        model = ChatSession
        fields = [
            'id', 'room', 'user_id', 'user_name', 'user_email',
            'user_role', 'started_at', 'ended_at', 'is_active', 'duration'
        ]
        read_only_fields = ['id', 'started_at']