from django.conf import settings
import jwt
from datetime import datetime, timedelta, timezone

def generate_access_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + settings.JWT_ACCESS_TOKEN_LIFETIME,
        'iat': datetime.now(timezone.utc),
        'type': 'access'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def generate_refresh_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + settings.JWT_REFRESH_TOKEN_LIFETIME,
        'iat': datetime.now(timezone.utc),
        'type': 'refresh'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')