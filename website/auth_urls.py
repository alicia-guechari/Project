from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('', include('dj_rest_auth.urls')),    
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
