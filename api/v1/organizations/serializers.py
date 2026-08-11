from rest_framework import serializers
from organizations.models import Organization, Membership

class MembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Membership
        fields = ['id', 'username', 'role', 'joined_at']

class OrganizationSerializer(serializers.ModelSerializer):
    members = MembershipSerializer(source='memberships', many=True, read_only=True)
    
    class Meta:
        model = Organization
        fields = ['id', 'uid', 'name', 'invite_code', 'created_at', 'members']