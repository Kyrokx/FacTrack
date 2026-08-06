from django.urls import path
from . import views

urlpatterns = [
    path('', views.organization_detail_view, name='api_organization_detail'),
    path('join/', views.join_organization_view, name='api_join_organization'),
    path('leave/', views.leave_organization_view, name='api_leave_organization'),
    path('members/', views.members_list_view, name='api_members_list'),
]