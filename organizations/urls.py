from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import * 

urlpatterns = [
    path('setup/', setup_view, name='setup'),
    path('create/', create_organization_view, name='create_organization'),
    path('join/', join_organization_view, name='join_organization'),
    path('organization/settings/', organization_settings_view, name='organization_settings'),
    path('organization/member/<int:membership_id>/promote/', promote_member_view, name='promote_member'),
    path('organization/member/<int:membership_id>/remove/', remove_member_view, name='remove_member'),
    path('organization/leave/', leave_organization_view, name='leave_organization'),
]
