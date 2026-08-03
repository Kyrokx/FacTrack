from django.contrib import admin
from .models import Bill,Organization, Membership   
# Register your models here.
admin.site.site_header = "Factrack Administration"
admin.site.site_title = "Factrack Admin Portal"
admin.site.index_title = "Welcome to Factrack Portal"
admin.site.register(Bill)
admin.site.register(Organization)
admin.site.register(Membership)