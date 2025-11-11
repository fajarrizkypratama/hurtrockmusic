"""
Health check utilities for chat microservice
"""
import redis
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


def check_redis_connection():
    """
    Check if Redis connection is working
    """
    try:
        redis_url = getattr(settings, 'REDIS_URL', None)
        if not redis_url:
            return {
                'status': 'skipped',
                'message': 'Redis not configured, using InMemory channel layer'
            }
        
        # Try to connect to Redis
        r = redis.from_url(redis_url)
        r.ping()
        
        return {
            'status': 'healthy',
            'message': 'Redis connection successful'
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy', 
            'message': f'Redis connection failed: {str(e)}'
        }


def check_database_connection():
    """
    Check if database connection is working
    """
    try:
        from .models import ChatRoom
        ChatRoom.objects.count()
        
        return {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_detailed(request):
    """
    Detailed health check endpoint
    """
    checks = {
        'database': check_database_connection(),
        'redis': check_redis_connection(),
    }
    
    # Overall status
    overall_status = 'healthy'
    for check_name, check_result in checks.items():
        if check_result['status'] == 'unhealthy':
            overall_status = 'unhealthy'
            break
        elif check_result['status'] == 'skipped' and overall_status == 'healthy':
            overall_status = 'degraded'
    
    return JsonResponse({
        'service': 'chat_microservice',
        'version': '1.0.0', 
        'timestamp': timezone.now().isoformat(),
        'overall_status': overall_status,
        'checks': checks
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_simple(request):
    """
    Simple health check endpoint
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'chat_microservice',
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat()
    })
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

@csrf_exempt
def health_check(request):
    """Health check endpoint for Django service"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        
        return JsonResponse({
            'status': 'healthy',
            'service': 'django-chat',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'service': 'django-chat',
            'error': str(e)
        }, status=500)
