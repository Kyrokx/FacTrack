from django.urls import path
from bills.views import * 


urlpatterns = [
    path('', home_view, name='home'),
    path('add/', add_bills, name='add_bills'),
    path('bills/', bills_list, name='bills_list'),
    path('bills/<int:id>/', bill_detail, name='bill_detail'),
    path('export/csv/', export_bills_csv, name='export_csv'),
    path('export/pdf/', export_bills_pdf, name='export_pdf'),
    path('edit/<int:id>/', edit_bill, name='edit_bill'),
    path('delete/<int:id>/', delete_bill, name='delete_bill'),
    path('toggle/<int:id>/', toggle_bill, name='toggle_bill'),
]
