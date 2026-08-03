from django.db import models
from django.contrib.auth.models import User
import uuid
import secrets

def generate_invite_code():
    return 'FAM-' + secrets.token_hex(3).upper()

class Organization(models.Model):


    
    uid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    invite_code = models.CharField(max_length=10, unique=True, default=generate_invite_code)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.uid})"



class Membership(models.Model):

    TYPE_CHOICES = [
            ('admin', 'admin'),
            ('member', 'member'),
        ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=TYPE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"


class Bill(models.Model):
    TYPE_CHOICES = [
        ('SONABEL', 'SONABEL'),
        ('ONEA', 'ONEA'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    period = models.DateField()
    deadline = models.DateField()
    price_total = models.DecimalField(max_digits=10, decimal_places=0)
    previous_index = models.IntegerField()
    new_index = models.IntegerField()
    total_consumption = models.IntegerField()
    paid = models.BooleanField(default=False)
    organization = models.ForeignKey('Organization', null=True, blank=True, on_delete=models.SET_NULL, related_name='bills')

    def __str__(self):
        return f"{self.type} - {self.period.strftime('%m-%Y')}"

    class Meta:
        ordering = ['-period']