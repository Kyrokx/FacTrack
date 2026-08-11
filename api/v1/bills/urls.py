from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list_view, name='api_bill_list'),
    path('create/', views.bill_create_view, name='api_bill_create'),
    path('<int:id>/', views.bill_detail_view, name='api_bill_detail'),
    path('<int:id>/update/', views.bill_update_view, name='api_bill_update'),
    path('<int:id>/delete/', views.bill_delete_view, name='api_bill_delete'),
    path('<int:id>/toggle/', views.bill_toggle_view, name='api_bill_toggle'),
]