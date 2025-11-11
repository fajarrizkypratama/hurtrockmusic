"""
REST API views for chat microservice
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import ChatRoom, ChatMessage, ChatSession
from .serializers import ChatRoomSerializer, ChatMessageSerializer, ChatSessionSerializer
from .permissions import IsAdminOrStaff, IsOwnerOrAdmin

# Assuming jwt_required and logger are imported from appropriate modules
# For demonstration purposes, let's mock them if not provided
try:
    from rest_framework_simplejwt.exceptions import TokenBackendError
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.decorators import jwt_required
except ImportError:
    # Mock classes/decorators if JWT is not installed or configured
    class TokenBackendError(Exception): pass
    class JWTAuthentication:
        def authenticate(self, request): return None
    def jwt_required(func): return func

import logging
logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ChatRoom model
    """
    queryset = ChatRoom.objects.filter(is_active=True)
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for ChatMessage model
    """
    queryset = ChatMessage.objects.filter(is_deleted=False)
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Filter messages by room if specified"""
        queryset = super().get_queryset()
        room_name = self.request.query_params.get('room', None)
        if room_name:
            queryset = queryset.filter(room__name=room_name)
        return queryset.order_by('-created_at')


class ChatRoomMessagesView(APIView):
    """Get messages for a specific chat room"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, room_name):
        """Get messages for room"""
        try:
            room = get_object_or_404(ChatRoom, name=room_name)
            messages = ChatMessage.objects.filter(
                room=room,
                is_deleted=False
            ).order_by('created_at')  # Oldest first for chat display

            # If no pagination needed, return all messages
            if 'page' not in request.query_params:
                serializer = ChatMessageSerializer(messages, many=True)
                return Response({
                    'results': serializer.data,
                    'count': messages.count()
                })

            # Otherwise use pagination
            paginator = self.pagination_class()
            paginated_messages = paginator.paginate_queryset(messages, request)
            serializer = ChatMessageSerializer(paginated_messages, many=True)

            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            print(f"Error getting room messages: {e}")
            return Response(
                {'error': f'Gagal mengambil pesan: {str(e)}', 'results': []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JoinChatRoomView(APIView):
    """Join or create a chat room"""
    permission_classes = [IsAuthenticated]

    def post(self, request, room_name):
        """Join or create chat room"""
        try:
            user = request.user

            # Get or create room
            room, created = ChatRoom.objects.get_or_create(
                name=room_name,
                defaults={'is_active': True}
            )

            # Create or update chat session
            session, session_created = ChatSession.objects.get_or_create(
                room=room,
                user_id=user.id,
                is_active=True,
                defaults={
                    'user_name': user.name,
                    'started_at': timezone.now()
                }
            )

            return Response({
                'room_id': room.id,
                'room_name': room.name,
                'session_id': session.id,
                'message': f'Successfully joined room {room_name}',
                'room_created': created,
                'session_created': session_created
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Gagal join room: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TagProductView(APIView):
    """Tag a product to a chat message"""
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        """Tag product to message"""
        try:
            message = get_object_or_404(ChatMessage, id=message_id)
            product_id = request.data.get('product_id')

            if not product_id:
                return Response(
                    {'error': 'product_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            message.product_id = product_id
            message.save(update_fields=['product_id'])

            serializer = ChatMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Gagal tag produk: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PendingChatsView(APIView):
    """Get pending chat statistics for admin"""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request):
        """Get pending chat count and recent messages"""
        try:
            # Count unread messages from buyers
            pending_count = ChatMessage.objects.filter(
                is_read=False,
                sender_type='buyer',
                is_deleted=False
            ).count()

            # Get recent unread messages
            recent_messages = ChatMessage.objects.filter(
                is_read=False,
                sender_type='buyer',
                is_deleted=False
            ).order_by('-created_at')[:10]

            messages_data = ChatMessageSerializer(recent_messages, many=True).data

            return Response({
                'pending_count': pending_count,
                'recent_messages': messages_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Gagal mengambil data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatStatsView(APIView):
    """Get chat statistics for admin dashboard"""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request):
        """Get comprehensive chat statistics"""
        try:
            # Basic counts
            total_rooms = ChatRoom.objects.count()
            total_messages = ChatMessage.objects.filter(is_deleted=False).count()
            active_sessions = ChatSession.objects.filter(is_active=True).count()

            # Messages by type
            messages_by_type = ChatMessage.objects.filter(
                is_deleted=False
            ).values('sender_type').annotate(
                count=Count('id')
            ).order_by('sender_type')

            # Recent activity (last 7 days) - using TruncDate instead of deprecated extra()
            from django.db.models import TruncDate
            week_ago = timezone.now() - timezone.timedelta(days=7)
            recent_activity = ChatMessage.objects.filter(
                created_at__gte=week_ago,
                is_deleted=False
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')

            # Top active rooms - consistent message counting (exclude deleted)
            top_rooms = ChatRoom.objects.annotate(
                message_count=Count('messages', filter=Q(messages__is_deleted=False))
            ).order_by('-message_count')[:5]

            top_rooms_data = []
            for room in top_rooms:
                last_active_message = room.messages.filter(is_deleted=False).order_by('-created_at').first()
                top_rooms_data.append({
                    'name': room.name,
                    'message_count': room.message_count,
                    'last_message': last_active_message.formatted_created_at if last_active_message else None
                })

            return Response({
                'total_rooms': total_rooms,
                'total_messages': total_messages,
                'active_sessions': active_sessions,
                'messages_by_type': list(messages_by_type),
                'recent_activity': list(recent_activity),
                'top_rooms': top_rooms_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Gagal mengambil statistik: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BuyerChatRoomsView(APIView):
    """Get buyer chat rooms for admin interface"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get list of buyer chat rooms with search functionality"""
        try:
            search_query = request.query_params.get('search', '').strip()

            # Get buyer rooms (exclude support room)
            rooms_query = ChatRoom.objects.filter(
                buyer_id__isnull=False,
                is_active=True
            ).exclude(name='support_room')

            # Apply search filter
            if search_query:
                from django.db import models as django_models
                rooms_query = rooms_query.filter(
                    django_models.Q(buyer_name__icontains=search_query) |
                    django_models.Q(buyer_email__icontains=search_query)
                )

            # Order by latest message
            from django.db.models import Max
            rooms = rooms_query.annotate(
                last_message_time=Max('messages__created_at')
            ).order_by('-last_message_time', '-created_at')

            rooms_data = []
            for room in rooms:
                last_message = room.last_message
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'buyer_id': room.buyer_id,
                    'buyer_name': room.buyer_name,
                    'buyer_email': room.buyer_email,
                    'unread_count': room.unread_messages_count,
                    'message_count': room.message_count,
                    'last_message': {
                        'content': last_message.message[:50] + '...' if last_message and len(last_message.message) > 50 else last_message.message if last_message else None,
                        'timestamp': last_message.created_at.isoformat() if last_message else None,
                        'sender_type': last_message.sender_type if last_message else None
                    } if last_message else None,
                    'created_at': room.created_at.isoformat()
                })

            return Response({
                'rooms': rooms_data,
                'total_count': len(rooms_data)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Gagal mengambil daftar chat: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MarkMessagesAsReadView(APIView):
    """Mark messages as read in a room"""
    permission_classes = [IsAuthenticated]

    def post(self, request, room_name):
        """Mark all unread messages in room as read"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            room = get_object_or_404(ChatRoom, name=room_name)
            user = request.user if hasattr(request, 'user') else request.jwt_user

            # Get unread messages before marking as read
            unread_messages = ChatMessage.objects.filter(
                room=room,
                is_read=False
            )

            message_ids = list(unread_messages.values_list('id', flat=True))

            # Mark unread messages as read
            updated_count = unread_messages.update(is_read=True)

            # Send notification to room about read status
            if updated_count > 0:
                channel_layer = get_channel_layer()
                room_group_name = f'chat_{room_name}'
                
                async_to_sync(channel_layer.group_send)(
                    room_group_name,
                    {
                        'type': 'notification_message',
                        'notification': {
                            'type': 'messages_read',
                            'room_name': room_name,
                            'reader_id': user.get('user_id') if isinstance(user, dict) else user.id,
                            'reader_name': user.get('name') if isinstance(user, dict) else user.name,
                            'message_ids': message_ids,
                            'count': updated_count
                        }
                    }
                )

            return Response({
                'message': 'Messages marked as read',
                'count': updated_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'Error marking messages as read: {str(e)}', exc_info=True)
            return Response(
                {'error': f'Gagal menandai pesan sebagai dibaca: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def get_buyer_rooms(request):
    """Get all chat rooms with buyer information for admin"""
    try:
        # Check authentication
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)

        # Get user data from JWT
        user_data = getattr(request, 'jwt_user', {})
        user_role = user_data.get('role', 'buyer')

        # Check if user is admin or staff
        if user_role not in ['admin', 'staff']:
            return Response({'error': 'Admin access required'}, status=403)

        search_query = request.GET.get('search', '').strip()

        # Build the query
        rooms_query = ChatRoom.objects.select_related().prefetch_related('messages')

        if search_query:
            rooms_query = rooms_query.filter(
                Q(buyer_name__icontains=search_query) |
                Q(buyer_email__icontains=search_query) |
                Q(name__icontains=search_query)
            )

        rooms = rooms_query.order_by('-created_at')

        # Serialize the data
        rooms_data = []
        for room in rooms:
            last_message = room.messages.first()
            unread_count = room.messages.filter(is_read=False, sender_type='buyer').count()

            room_data = {
                'id': room.id,
                'name': room.name,
                'buyer_id': room.buyer_id,
                'buyer_name': room.buyer_name or 'Unknown User',
                'buyer_email': room.buyer_email or '',
                'created_at': room.created_at.isoformat() if room.created_at else None,
                'is_active': room.is_active,
                'unread_count': unread_count,
                'last_message': {
                    'content': last_message.message if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'sender_type': last_message.sender_type if last_message else '',
                } if last_message else None,
            }
            rooms_data.append(room_data)

        return Response({
            'rooms': rooms_data,
            'total_count': len(rooms_data)
        })

    except Exception as e:
        logger.error(f"Error in get_buyer_rooms: {str(e)}")
        return Response({'error': 'Internal server error', 'rooms': [], 'total_count': 0}, status=500)


@api_view(['GET'])
@jwt_required
def get_admin_rooms(request):
    """Get all chat rooms for admin (alias for get_buyer_rooms)"""
    return get_buyer_rooms(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """Send a chat message via REST API"""
    try:
        room_name = request.data.get('room_name')
        message = request.data.get('message')
        product_id = request.data.get('product_id')
        
        if not room_name or not message:
            return Response({'error': 'room_name and message are required'}, status=400)
        
        # Get or create room
        room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            defaults={'is_active': True}
        )
        
        # Create message
        chat_message = ChatMessage.objects.create(
            room=room,
            user_id=request.user.get('id', 0),
            user_name=request.user.get('name', 'Anonymous'),
            user_email=request.user.get('email', ''),
            message=message,
            sender_type=request.user.get('role', 'buyer'),
            product_id=product_id
        )
        
        serializer = ChatMessageSerializer(chat_message)
        return Response(serializer.data, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_token(request):
    """Get JWT token for WebSocket authentication"""
    try:
        # In a real implementation, you'd generate a token here
        # For now, we'll return a success response
        return Response({
            'token': 'placeholder_token',
            'user_id': request.user.get('id'),
            'room_name': request.GET.get('room_name', 'general')
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_room_messages(request, room_name):
    """Get messages for a specific room"""
    try:
        room = get_object_or_404(ChatRoom, name=room_name)
        messages = ChatMessage.objects.filter(
            room=room,
            is_deleted=False
        ).order_by('created_at')
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response({'results': serializer.data})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_messages_read(request, room_name):
    """Mark messages as read in a room"""
    try:
        room = get_object_or_404(ChatRoom, name=room_name)
        ChatMessage.objects.filter(
            room=room,
            is_read=False
        ).update(is_read=True)
        
        return Response({'message': 'Messages marked as read'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def ws_test(request):
    """WebSocket test endpoint"""
    return Response({
        'message': 'WebSocket service is available',
        'endpoint': '/ws/chat/<room_name>/'
    })


@api_view(['GET'])
def get_room_messages_api(request, room_name):
    """API endpoint for getting room messages - alternative to class-based view"""
    try:
        # Check authentication
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return Response({'error': 'Authentication required', 'results': []}, status=401)

        room = get_object_or_404(ChatRoom, name=room_name)
        messages = ChatMessage.objects.filter(
            room=room,
            is_deleted=False
        ).order_by('created_at')  # Oldest first for chat display

        # If no pagination needed, return all messages
        if 'page' not in request.query_params:
            serializer = ChatMessageSerializer(messages, many=True)
            return Response({
                'results': serializer.data,
                'count': messages.count()
            })

        # Otherwise use pagination
        paginator = StandardResultsSetPagination()
        paginated_messages = paginator.paginate_queryset(messages, request)
        serializer = ChatMessageSerializer(paginated_messages, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        logger.error(f"Error getting room messages: {e}")
        return Response(
            {'error': f'Gagal mengambil pesan: {str(e)}', 'results': []},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'chat_microservice',
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat()
    })