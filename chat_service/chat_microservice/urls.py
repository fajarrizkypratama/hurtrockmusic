"""
URL configuration for chat_microservice project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from chat.health import health_check

def chat_service_info(request):
    """Root endpoint info for chat microservice"""
    return JsonResponse({
        'service': 'Hurtrock Chat Microservice',
        'status': 'active',
        'version': '1.0.0',
        'endpoints': {
            'api': '/api/',
            'admin': '/admin/',
            'health': '/health/',
            'websocket': 'ws://[domain]/ws/chat/{room_name}/'
        }
    })

urlpatterns = [
    path('', chat_service_info, name='chat_service_info'),
    path('admin/', admin.site.urls),
    path('api/', include('chat.urls')),
    path('health/', health_check, name='health_check'),
]