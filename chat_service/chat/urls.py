
"""
URL configuration for chat app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rooms', views.ChatRoomViewSet)
router.register(r'messages', views.ChatMessageViewSet)

urlpatterns = [
    # Router patterns
    path('', include(router.urls)),
    
    # Custom endpoints
    path('rooms/<str:room_name>/messages/', views.ChatRoomMessagesView.as_view(), name='room-messages'),
    path('rooms/<str:room_name>/messages/api/', views.get_room_messages_api, name='room-messages-api'),
    path('rooms/<str:room_name>/join/', views.JoinChatRoomView.as_view(), name='join-room'),
    path('rooms/<str:room_name>/mark-read/', views.MarkMessagesAsReadView.as_view(), name='mark-read'),
    
    # Admin endpoints
    path('admin/buyer-rooms/', views.get_buyer_rooms, name='admin-buyer-rooms'),
    path('admin/rooms/', views.get_admin_rooms, name='admin-rooms'),
    path('admin/stats/', views.ChatStatsView.as_view(), name='chat-stats'),
    path('admin/pending/', views.PendingChatsView.as_view(), name='pending-chats'),
    
    # Message operations
    path('messages/<int:message_id>/tag-product/', views.TagProductView.as_view(), name='tag-product'),
    path('send-message/', views.send_message, name='send-message'),
    
    # Utility endpoints
    path('token/', views.get_chat_token, name='chat-token'),
    path('ws-test/', views.ws_test, name='ws-test'),
    path('health/', views.health_check, name='health-check'),
]
