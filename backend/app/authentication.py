from rest_framework import authentication, exceptions
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
from datetime import datetime

User = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None
        try:
            token = token.split(' ')[1]
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
                )
            user_id = payload['user_id']
            user = User.objects.get(id=user_id)
            
            if not user.is_active:
                raise exceptions.AuthenticationFailed('User is inactive')
            
            return (user, None)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token is invalid')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding token')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        except Exception as e:
            raise exceptions.AuthenticationFailed(e)
        
        def authenticate_header(self, request):
            return 'Bearer'
            