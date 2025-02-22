from rest_framework import authentication, exceptions
from rest_framework.authentication import get_authorization_header
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
from datetime import datetime
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)
User = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            # Get token from cookies or Authorization header
            token = request.COOKIES.get('access_token')
            
            if not token:
                auth_header = get_authorization_header(request).decode('utf-8')
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]

            if not token:
                return None
            
            if cache.get(f'blacklist_access_{token}'):
                raise exceptions.AuthenticationFailed('Token is blacklisted')

            # Clean up token if it starts with 'Bearer'
            if token.startswith('Bearer '):
                token = token.split(' ')[1]

            # Decode and validate token
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed('Token has expired')
            except (jwt.InvalidTokenError, jwt.DecodeError):
                raise exceptions.AuthenticationFailed('Invalid token')

            # Validate token type and expiration
            if payload.get('type') != 'access':
                raise exceptions.AuthenticationFailed('Invalid token type')

            if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
                raise exceptions.AuthenticationFailed('Token has expired')

            # Validate and return user
            user_id = payload.get('user_id')
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token payload')

            try:
                user = User.objects.get(id=user_id)
                if not user.is_active:
                    raise exceptions.AuthenticationFailed('User is inactive')
                return (user, None)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not found')

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise exceptions.AuthenticationFailed(str(e))

    def authenticate_header(self, request):
        return 'Bearer'