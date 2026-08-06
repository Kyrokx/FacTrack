from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from organizations.models import Organization, Membership
from .serializers import OrganizationSerializer,MembershipSerializer

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_organization_view(request):
    invite_code = request.data.get('invite_code')
    
    if hasattr(request.user, 'membership'):
        return Response(
            {'error': 'Vous appartenez déjà à une organisation.'},
            status=status.HTTP_208_ALREADY_REPORTED
        )
    try:
        organization = Organization.objects.get(invite_code=invite_code)
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Le code d\'invitation n\'existe pas.'},
            status=status.HTTP_400_BAD_REQUEST
        
        )
        
        
    

    try:
        Membership.objects.create(user=request.user, organization=organization, role='member')
        return Response({
                    'message': 'Vous avez rejoins l\'organisation',
                }, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response(
            {'error': 'Une erreur est survenue.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_organization_view(request):
    if not hasattr(request.user, 'membership'):
            return Response(
                {'error': 'Vous n\'appartenez à aucune organisation.'},
                status=status.HTTP_404_NOT_FOUND
            )
               

    try:
        Membership.objects.filter(user=request.user).delete()
        return Response({
                    'message': 'Vous avez quitté l\'organisation',
                }, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response(
            {'error': 'Une erreur est survenue.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def members_list_view(request):
    if not hasattr(request.user, 'membership'):
        return Response(
            {'error': 'Vous n\'appartenez à aucune organisation.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    organization = request.user.membership.organization
    members = organization.memberships.all()
    serializer = MembershipSerializer(members, many=True)
    return Response(serializer.data)