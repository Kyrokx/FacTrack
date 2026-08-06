from django.urls import path
from . import views

urlpatterns = [
    path('', views.organization_detail_view, name='api_organization_detail'),
]