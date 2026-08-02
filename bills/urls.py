from django.urls import path

from . import views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('add/', views.add_bills, name='add_bills'),
    path('bills/', views.bills_list, name='bills_list'),
    path('bills/<int:id>/', views.bill_detail, name='bill_detail'),
    path('edit/<int:id>/', views.edit_bill, name='edit_bill'),
    path('delete/<int:id>/', views.delete_bill, name='delete_bill'),
    path('toggle/<int:id>/', views.toggle_bill, name='toggle_bill'),
    path('export/csv/', views.export_bills_csv, name='export_csv'),
    path('export/pdf/', views.export_bills_pdf, name='export_pdf'),
]
