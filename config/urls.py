"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from bills.views import home_view,add_bills,bills_list,toggle_bill,edit_bill,delete_bill,export_bills_csv,export_bills_pdf,bill_detail,signup_view,setup_view


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', signup_view, name='signup'),
    path('setup/', setup_view, name='setup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', home_view, name='home'),
    path('add/', add_bills, name='add_bills'),
    path('bills/', bills_list, name='bills_list'),
    path('bills/<int:id>/', bill_detail, name='bill_detail'),
    path('export/csv/', export_bills_csv, name='export_csv'),
    path('export/pdf/', export_bills_pdf, name='export_pdf'),
    path('edit/<int:id>/', edit_bill, name='edit_bill'),
    path('delete/<int:id>/', delete_bill, name='delete_bill'),
    path('toggle/<int:id>/', toggle_bill, name='toggle_bill'),
    path('admin/', admin.site.urls),
]
