from django.urls import path
from . import views

urlpatterns = [
    path('refresh-token', views.CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('me', views.MeView.as_view(), name='me'),
    path('signup', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
]