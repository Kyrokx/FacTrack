from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.setup_view, name='setup'),
    path('create/', views.create_organization_view, name='create_organization'),
    path('join/', views.join_organization_view, name='join_organization'),
    path('organization/settings/', views.organization_settings_view, name='organization_settings'),
    path('organization/member/<int:membership_id>/promote/', views.promote_member_view, name='promote_member'),
    path('organization/member/<int:membership_id>/remove/', views.remove_member_view, name='remove_member'),
    path('organization/leave/', views.leave_organization_view, name='leave_organization'),
]