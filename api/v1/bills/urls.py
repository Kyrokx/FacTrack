from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list_view, name='api_bill_list'),
]