"""
JWT Authentication for Django Chat Service
"""
import jwt
import json
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser


class JWTUser:
    """Simple user object for JWT authentication"""
    def __init__(self, user_data):
        self.id = user_data.get('user_id', 0)
        self.email = user_data.get('email', '')
        self.name = user_data.get('name', '')
        self.role = user_data.get('role', 'buyer')
        self.is_authenticated = True
        self.is_anonymous = False

    def __str__(self):
        return f"{self.name} ({self.email})"


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for chat service
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Create user object from JWT payload
            user = JWTUser(payload)

            # Store user data in request for views
            request.jwt_user = payload

            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'Bearer'


def get_user_from_token(token):
    """
    Helper function to get user data from JWT token
    """
    try:
        auth = JWTAuthentication()
        # The original get_user_from_payload was removed and replaced by JWTUser class
        # We need to decode the token and then create a JWTUser object
        payload = jwt.decode(token, getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY), algorithms=['HS256'])
        return JWTUser(payload)
    except Exception as e:
        print(f"Error decoding JWT token: {str(e)}")
        return None


class MockRequest:
    """Mock request for token validation"""
    def __init__(self, token=None):
        self.GET = {'token': token} if token else {}
        self.META = {'HTTP_AUTHORIZATION': f'Bearer {token}'} if token else {}

def authenticate_websocket(token):
    """
    Authenticate WebSocket connection using JWT token
    """
    try:
        if not token:
            return None

        auth = JWTAuthentication()
        mock_request = MockRequest(token)
        result = auth.authenticate(mock_request)

        if result:
            user_data, _ = result
            return user_data
        return None
    except Exception as e:
        print(f"WebSocket authentication error: {str(e)}")
        return None