# accounts/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    # Class-based registration view
    path('register/', RegisterView.as_view(), name='register'),
    # Class-based login view (customized)
    path('login/', LoginView.as_view(), name='login'),
    # Class-based logout view (customized)
    path('logout/', LogoutView.as_view(), name='logout'),
]
