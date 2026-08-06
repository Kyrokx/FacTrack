from django.urls import path, include

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),
    path('bills/', include('api.v1.bills.urls')),
    path('organizations/', include('api.v1.organizations.urls')),
]