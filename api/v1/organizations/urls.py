from django.urls import path
from . import views

urlpatterns = [
    path('', views.organization_detail_view, name='api_organization_detail'),
    path('join/', views.join_organization_view, name='api_join_organization'),
    path('leave/', views.leave_organization_view, name='api_leave_organization'),
    path('members/', views.members_list_view, name='api_members_list'),
    path('create/', views.create_organization_view, name='api_create_organization'),
    path('members/<int:membership_id>/remove/', views.remove_member_view, name='api_remove_member'),
    path('members/<int:membership_id>/promote/', views.promote_member_view, name='api_promote_member'),
    path('regenerate-invite-code/', views.regenerate_invite_code_view, name='api_regenerate_invite_code'),

]