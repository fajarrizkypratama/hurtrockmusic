
"""
Chat models for the microservice
"""
from django.db import models
from django.utils import timezone


class ChatRoom(models.Model):
    """Chat room model"""
    name = models.CharField(max_length=100, unique=True, db_index=True)
    buyer_id = models.IntegerField(null=True, blank=True, db_index=True)
    buyer_name = models.CharField(max_length=255, null=True, blank=True)
    buyer_email = models.EmailField(max_length=254, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'chat_rooms'

    def __str__(self):
        if self.buyer_name:
            return f"Room: {self.buyer_name} ({self.buyer_email})"
        return f"Room: {self.name}"

    @property
    def message_count(self):
        """Get total message count for this room"""
        return self.messages.filter(is_deleted=False).count()

    @property
    def last_message(self):
        """Get the last message in this room"""
        return self.messages.filter(is_deleted=False).order_by('-created_at').first()

    @property
    def unread_messages_count(self):
        """Get count of unread messages"""
        return self.messages.filter(is_read=False, is_deleted=False).count()


class ChatMessage(models.Model):
    """Chat message model - matches Flask schema exactly"""
    SENDER_CHOICES = [
        ('buyer', 'Buyer'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]

    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', db_column='room_id')
    user_id = models.IntegerField(db_index=True)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField(max_length=254, blank=True, null=True)
    message = models.TextField()
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES, default='buyer')
    product_id = models.IntegerField(null=True, blank=True)
    media_url = models.CharField(max_length=500, null=True, blank=True, default=None, help_text="URL path to uploaded media file")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, null=True, blank=True, default=None, help_text="Type of media: image or video")
    media_filename = models.CharField(max_length=255, null=True, blank=True, default=None, help_text="Original filename of uploaded media")
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'chat_messages'
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['is_read', 'sender_type']),
        ]

    def __str__(self):
        return f"{self.user_name}: {self.message[:50]}..."

    @property
    def formatted_created_at(self):
        """Format creation timestamp for display"""
        return self.created_at.strftime('%d/%m/%Y %H:%M')


class ChatSession(models.Model):
    """Chat session tracking model - matches Flask schema exactly"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='sessions', db_column='room_id')
    user_id = models.IntegerField(db_index=True)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField(max_length=254, blank=True, null=True)
    user_role = models.CharField(max_length=20, default='buyer')
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-started_at']
        db_table = 'chat_sessions'
        indexes = [
            models.Index(fields=['room', 'user_id']),
            models.Index(fields=['is_active', '-started_at']),
        ]

    def __str__(self):
        return f"Session: {self.user_name} in {self.room.name}"

    @property
    def duration(self):
        """Calculate session duration"""
        end_time = self.ended_at or timezone.now()
        return end_time - self.started_at
