from django.urls import path, include
from .views import RegisterView, LoginView, LogoutView, RefreshTokenView, UserView, GitHubAuthView, GoogleAuthView, TwoFactorDisableView, TwoFactorSetupView, TwoFactorVerifyView
# from . import views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('user/', UserView.as_view(), name='user'),
    path('oauth/github/', GitHubAuthView.as_view(), name='github'),
    path('oauth/google/', GoogleAuthView.as_view(), name='google'),
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa-verify'),
    path('2fa/disable/', TwoFactorDisableView.as_view(), name='2fa-disable'),
]