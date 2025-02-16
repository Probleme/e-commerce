from django.shortcuts import render

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import UserSerializer, RegisterSerializer
from .utils import generate_access_token, generate_refresh_token
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(email=email, password=password)
        
        if user is not None:
            if user.is_active:
                access_token = generate_access_token(user)
                refresh_token = generate_refresh_token(user)
                response = Response({
                    'message' : 'Login successful',
                    'user' : UserSerializer(user).data
                })
                response.set_cookie(
                    'access_token',
                    access_token,
                    httponly=True,
                    samesite='Lax',
                    max_age=3600 # 1 hour
                )
                response.set_cookie(
                    'refresh_token',
                    refresh_token,
                    httponly=True,
                    samesite='Lax',
                    max_age=3600 * 24 * 1 # 1 day
                )
                response.set_cookie(
                    'logged_in',
                    'true',
                    httponly=False,
                    samesite='Lax',
                    max_age=3600 * 24 * 1 # 1 day
                )
                return response
            else:
                return Response({
                    'error' : 'Account is disabled'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'error' : 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        response = Response()
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.delete_cookie('logged_in')
        response.data = {
            'message' : 'Logout successful'
        }
        return response
    
class RefreshView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error' : 'Refresh token not provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            if payload['type'] != 'refresh':
                return Response({
                    'error' : 'Invalid token type'
                }, status=status.HTTP_400_BAD_REQUEST)
        
            user = User.objects.get(id=payload['user_id'])
            
            access_token = generate_access_token(user)
            
            response = Response({
                'message' : 'Refresh successful'
            })
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                samesite='Lax',
                max_age=3600 # 1 hour
            )
            
            return response
        
        except jwt.ExpiredSignatureError:
            return Response({
                'error' : 'Refresh token has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return Response({
                'error' : 'Invalid refresh token'
            }, status=status.HTTP_400_BAD_REQUEST)