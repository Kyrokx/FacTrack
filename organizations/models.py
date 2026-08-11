from django.db import models
from django.contrib.auth.models import User
import uuid
import secrets
# bills/models.py

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
            ('owner', 'owner'),
            ('admin', 'admin'),
            ('member', 'member'),
        ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=TYPE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"