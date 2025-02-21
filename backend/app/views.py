from django.shortcuts import render

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import UserSerializer, RegisterSerializer
from .utils import generate_access_token, generate_refresh_token, verify_access_token
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from .authentication import JWTAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()

class UserView(APIView):
    permission_classes = []
    authentication_classes = []
    def get(self, request):
        try:
            # Get access token from cookies
            access_token = request.COOKIES.get('access_token')
            
            if not access_token:
                return Response({
                    'error': 'No access token provided'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Verify the access token and get user_id
            user_id = verify_access_token(access_token)
            
            if not user_id:
                return Response({
                    'error': 'Invalid or expired token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user from database
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user is active
            if not user.is_active:
                return Response({
                    'error': 'User account is disabled'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Return user data
            return Response(UserSerializer(user).data)
            
        except Exception as e:
            return Response({
                'error': 'Authentication failed'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
    
class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Registration successful',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response({
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                return Response({
                    'error': 'Email and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(email=email, password=password)
            
            if user is not None:
                if user.is_active:
                    access_token = generate_access_token(user)
                    refresh_token = generate_refresh_token(user)
                    response = Response({
                        'message': 'Login successful',
                        'user': UserSerializer(user).data
                    })
                    response.set_cookie(
                        'access_token',
                        access_token,
                        httponly=True,
                        samesite='Lax',
                        max_age=3600  # 1 hour
                    )
                    response.set_cookie(
                        'refresh_token',
                        refresh_token,
                        httponly=True,
                        samesite='Lax',
                        max_age=3600 * 24  # 1 day
                    )
                    return response
                else:
                    return Response({
                        'error': 'Account is disabled'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({
                    'error': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({
                'error': 'An error occurred during login. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        response = Response()
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.data = {
            'message' : 'Logout successful'
        }
        return response
    
class RefreshTokenView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token not provided'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            if payload['type'] != 'refresh':
                raise jwt.InvalidTokenError('Invalid token type')

            user = User.objects.get(id=payload['user_id'])
            access_token = generate_access_token(user)
            
            response = Response({
                'message': 'Token refresh successful'
            })
            
            response.set_cookie(
                'access_token',
                access_token,
                max_age=3600,
                httponly=True,
                samesite='Lax',
                secure=True
            )
            
            return response

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)