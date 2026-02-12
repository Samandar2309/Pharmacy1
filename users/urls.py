from django.urls import path
from .views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    LogoutView,
    ProfileView,
    ForgotPasswordView,
    ResetPasswordView,
    index  # minimal front
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', index, name='index'),  # front sahifa
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # AUTH
    path('register/', RegisterView.as_view(), name='user-register'),
    path('verify/', VerifyOTPView.as_view(), name='user-verify'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),

    # PROFILE
    path('me/', ProfileView.as_view(), name='user-profile'),

    # PASSWORD
    path('password/forgot/', ForgotPasswordView.as_view(), name='password-forgot'),
    path('password/reset/', ResetPasswordView.as_view(), name='password-reset'),
]
