from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import UserSerializer, RegisterSerializer
from .utils import generate_access_token, generate_refresh_token, verify_access_token
import jwt
from django.contrib.auth import get_user_model
from .authentication import JWTAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import requests
import logging
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth import logout as django_logout
from django.core.cache import cache
import pyotp
import qrcode
import base64
from io import BytesIO
import secrets

logger = logging.getLogger(__name__)

User = get_user_model()

class TwoFactorSetupView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """Generate new 2FA secret and QR code"""
        user = request.user
        
        if user.two_factor_enabled:
            return Response({
                'error': '2FA is already enabled'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate new secret
        secret = pyotp.random_base32()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(8)]
        
        # Store secret and backup codes temporarily in session
        request.session['temp_2fa_secret'] = secret
        request.session['temp_backup_codes'] = backup_codes

        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            user.email, 
            issuer_name="YourApp"
        )

        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode()

        return Response({
            'secret': secret,
            'qr_code': qr_code,
            'backup_codes': backup_codes
        })

    def post(self, request):
        """Verify and enable 2FA"""
        user = request.user
        code = request.data.get('code')
        
        # Get secret from session
        secret = request.session.get('temp_2fa_secret')
        backup_codes = request.session.get('temp_backup_codes')

        if not secret or not code:
            return Response({
                'error': 'Invalid setup session'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify code
        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            # Enable 2FA
            user.two_factor_secret = secret
            user.two_factor_enabled = True
            user.two_factor_backup_codes = backup_codes
            user.save()

            # Clear temporary session data
            del request.session['temp_2fa_secret']
            del request.session['temp_backup_codes']

            return Response({
                'message': '2FA enabled successfully',
                'backup_codes': backup_codes
            })

        return Response({
            'error': 'Invalid verification code'
        }, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorVerifyView(APIView):
    """Verify 2FA code during login"""
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            code = request.data.get('code')

            if not user_id or not code:
                return Response({
                    'error': 'User ID and verification code are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if user is in authentication process
            cache_key = f'2fa_auth_{user_id}'
            if not cache.get(cache_key):
                return Response({
                    'error': 'Invalid or expired authentication session'
                }, status=status.HTTP_401_UNAUTHORIZED)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'Invalid user'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not user.two_factor_enabled:
                return Response({
                    'error': '2FA is not enabled for this user'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if it's a backup code
            if code in user.two_factor_backup_codes:
                # Remove used backup code
                user.two_factor_backup_codes.remove(code)
                user.save()
                
                # Clear the 2FA session
                cache.delete(cache_key)

                # Generate tokens and complete login
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
                    max_age=3600
                )
                response.set_cookie(
                    'refresh_token',
                    refresh_token,
                    httponly=True,
                    samesite='Lax',
                    max_age=3600 * 24
                )
                return response

            # Verify TOTP code
            totp = pyotp.TOTP(user.two_factor_secret)
            if totp.verify(code):
                # Clear the 2FA session
                cache.delete(cache_key)

                # Generate tokens and complete login
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
                    max_age=3600
                )
                response.set_cookie(
                    'refresh_token',
                    refresh_token,
                    httponly=True,
                    samesite='Lax',
                    max_age=3600 * 24
                )
                return response

            return Response({
                'error': 'Invalid verification code'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'error': 'An error occurred during verification'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TwoFactorDisableView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """Disable 2FA"""
        user = request.user
        code = request.data.get('code')

        if not user.two_factor_enabled:
            return Response({
                'error': '2FA is not enabled'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify code before disabling
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(code):
            user.two_factor_secret = None
            user.two_factor_enabled = False
            user.two_factor_backup_codes = []
            user.save()
            return Response({'message': '2FA disabled successfully'})

        return Response({
            'error': 'Invalid verification code'
        }, status=status.HTTP_400_BAD_REQUEST)

class GoogleAuthView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        code = request.data.get('code')
        
        if not code:
            return Response({
                'error': 'No code provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Exchange the code for access token
            token_url = 'https://oauth2.googleapis.com/token'
            data = {
                'code': code,
                'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                'redirect_uri': f"{request.headers.get('Origin', 'http://localhost:3000')}/oauth/google/callback",
                'grant_type': 'authorization_code'
            }

            # Get Google access token
            token_response = requests.post(token_url, data=data)
            token_data = token_response.json()

            if 'error' in token_data:
                return Response({
                    'error': token_data.get('error_description', 'Failed to obtain access token')
                }, status=status.HTTP_400_BAD_REQUEST)

            access_token = token_data.get('access_token')
            if not access_token:
                return Response({
                    'error': 'No access token received'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get user info from Google
            userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
            user_response = requests.get(
                userinfo_url,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if user_response.status_code != 200:
                return Response({
                    'error': 'Failed to get user data from Google'
                }, status=status.HTTP_400_BAD_REQUEST)

            google_user = user_response.json()

            email = google_user.get('email')
            if not email:
                return Response({
                    'error': 'No email found from Google'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get or create user
            User = get_user_model()
            try:
                username = email.split('@')[0]  # Use email prefix as username
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'is_active': True
                    }
                )

                # Update user's image if available
                picture = google_user.get('picture')
                if picture and (created or not user.image):
                    user.image = picture
                    user.save(update_fields=['image'])

            except IntegrityError:
                # Handle username conflict
                base_username = username
                counter = 1
                while True:
                    try:
                        username = f"{base_username}_{counter}"
                        user, created = User.objects.get_or_create(
                            email=email,
                            defaults={
                                'username': username,
                                'is_active': True
                            }
                        )
                        break
                    except IntegrityError:
                        counter += 1
                        if counter > 10:
                            raise

            # Generate JWT tokens
            jwt_access_token = generate_access_token(user)
            jwt_refresh_token = generate_refresh_token(user)
            
            response = Response({
                'message': 'Google login successful',
                'user': UserSerializer(user).data
            })
            
            response.set_cookie(
                'access_token',
                jwt_access_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=3600
            )
            response.set_cookie(
                'refresh_token',
                jwt_refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=3600 * 24
            )
            
            return response

        except requests.exceptions.RequestException as e:
            return Response({
                'error': 'Failed to communicate with Google'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GitHubAuthView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        code = request.data.get('code')
        
        if not code:
            return Response({
                'error': 'No code provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Exchange the code for an access token
            token_url = 'https://github.com/login/oauth/access_token'
            data = {
                'client_id': settings.SOCIAL_AUTH_GITHUB_KEY,
                'client_secret': settings.SOCIAL_AUTH_GITHUB_SECRET,
                'code': code
            }
            headers = {
                'Accept': 'application/json'
            }

            # Get GitHub access token
            token_response = requests.post(token_url, data=data, headers=headers)
            token_data = token_response.json()

            if 'error' in token_data:
                return Response({
                    'error': token_data.get('error_description', 'Failed to obtain access token')
                }, status=status.HTTP_400_BAD_REQUEST)

            access_token = token_data.get('access_token')
            if not access_token:
                return Response({
                    'error': 'No access token received'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user info from GitHub
            user_url = 'https://api.github.com/user'
            user_response = requests.get(
                user_url,
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
            )
            
            if user_response.status_code != 200:
                return Response({
                    'error': 'Failed to get user data from GitHub'
                }, status=status.HTTP_400_BAD_REQUEST)

            github_user = user_response.json()

            # Get user's email
            emails_url = 'https://api.github.com/user/emails'
            emails_response = requests.get(
                emails_url,
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
            )
            
            if emails_response.status_code != 200:
                return Response({
                    'error': 'Failed to get user emails from GitHub'
                }, status=status.HTTP_400_BAD_REQUEST)

            emails = emails_response.json()
            
            # Make sure emails is a list
            if not isinstance(emails, list):
                return Response({
                    'error': 'Invalid email data format from GitHub'
                }, status=status.HTTP_400_BAD_REQUEST)

            primary_email = None
            for email in emails:
                if isinstance(email, dict) and email.get('primary'):
                    primary_email = email.get('email')
                    break

            if not primary_email:
                primary_email = github_user.get('email')

            if not primary_email:
                return Response({
                    'error': 'No email found from GitHub'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get or create user
            User = get_user_model()
            try:
                username = github_user.get('login')
                if not username:
                    return Response({
                        'error': 'No username provided by GitHub'
                    }, status=status.HTTP_400_BAD_REQUEST)

                user, created = User.objects.get_or_create(
                    email=primary_email,
                    defaults={
                        'username': username,
                        'is_active': True
                    }
                )

                # Update user's image if available
                avatar_url = github_user.get('avatar_url')
                if avatar_url and (created or not user.image):
                    user.image = avatar_url
                    user.save(update_fields=['image'])

            except IntegrityError as e:
                logger.error(f"Database integrity error: {str(e)}")
                # Handle username conflict
                base_username = username
                counter = 1
                while True:
                    try:
                        username = f"{base_username}_{counter}"
                        user, created = User.objects.get_or_create(
                            email=primary_email,
                            defaults={
                                'username': username,
                                'is_active': True
                            }
                        )
                        break
                    except IntegrityError:
                        counter += 1
                        if counter > 10:
                            raise

            # Generate JWT tokens
            jwt_access_token = generate_access_token(user)
            jwt_refresh_token = generate_refresh_token(user)
            
            response = Response({
                'message': 'GitHub login successful',
                'user': UserSerializer(user).data
            })
            
            response.set_cookie(
                'access_token',
                jwt_access_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=3600
            )
            response.set_cookie(
                'refresh_token',
                jwt_refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=3600 * 24
            )
            
            return response

        except requests.exceptions.RequestException as e:
            return Response({
                'error': 'Failed to communicate with GitHub'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                if not user.is_active:
                    return Response({
                        'error': 'Account is disabled'
                    }, status=status.HTTP_401_UNAUTHORIZED)

                # Check if user has 2FA enabled
                if user.two_factor_enabled:
                    # Store authentication status in cache
                    cache_key = f'2fa_auth_{user.id}'
                    cache.set(cache_key, True, timeout=300)  # 5 minutes timeout
                    
                    return Response({
                        'requires_2fa': True,
                        'user_id': user.id,
                        'message': 'Please enter your 2FA code'
                    })

                # If no 2FA, proceed with normal login
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
        try:
            # Get the tokens from cookies
            access_token = request.COOKIES.get('access_token')
            refresh_token = request.COOKIES.get('refresh_token')

            # Blacklist the tokens
            if access_token:
                cache.set(f'blacklist_access_{access_token}', 'true', timeout=3600)
            if refresh_token:
                cache.set(f'blacklist_refresh_{refresh_token}', 'true', timeout=3600 * 24)

            # Perform Django logout
            django_logout(request)

            response = Response({
                'message': 'Successfully logged out'
            })

            # Delete cookies
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            # Add cache control headers
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

            return response

        except Exception as e:
            return Response({
                'error': 'An error occurred during logout'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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