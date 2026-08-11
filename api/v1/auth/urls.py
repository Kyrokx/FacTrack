from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.register_view, name='api_register'),
    path('login/', views.login_view, name='api_login'),
    path('logout/', views.logout_view, name='api_logout'),
    path('me/', views.about_me_view, name='api_about_me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
]