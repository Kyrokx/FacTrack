from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from organizations.models import Organization, Membership
from .serializers import OrganizationSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_detail_view(request):
    if not hasattr(request.user, 'membership'):
        return Response(
            {'error': 'Vous n\'appartenez à aucune organisation.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    organization = request.user.membership.organization
    serializer = OrganizationSerializer(organization)
    return Response(serializer.data)