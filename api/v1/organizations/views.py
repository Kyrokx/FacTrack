from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from organizations.models import Organization, Membership,generate_invite_code
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
               
               
    if request.user.membership.role == 'owner':
        return Response(
            {'error': 'Le propriétaire ne peut pas quitter le foyer.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        Membership.objects.filter(user=request.user).delete()
        return Response({
                    'message': 'Vous avez quitté l\'organisation',
                }, status=status.HTTP_200_OK)
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization_view(request,name):
    if hasattr(request.user, 'membership'):
            return Response(
                {'error': 'Vous appartenez déjà à une organisation.'},
                status=status.HTTP_208_ALREADY_REPORTED
            )
            
    if not name:
        return Response(
            {'error': 'Le nom de l\'organisation est requis.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    user = request.user

    try:
        organization = Organization.objects.create(name=name)
        Membership.objects.create(user=user, organization=organization, role='owner')
        return Response({
            'message': 'Organisation crée avec succes. '
            },
                        status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response(
                    {'error': 'Une erreur est survenue.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member_view(request, membership_id):
    if request.user.membership.role != 'owner':
        return Response(
            {'error': 'Seul le propriétaire peut supprimer des membres.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    membership = get_object_or_404(
        Membership,
        id=membership_id,
        organization=request.user.membership.organization
    )
    
    if membership.user == request.user:
        return Response(
            {'error': 'Vous ne pouvez pas vous supprimer vous-même.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if membership.role == 'owner':
        return Response(
            {'error': 'Vous ne pouvez pas supprimer un propriétaire.'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
        
    try: 
    
        membership.delete()
        return Response(
            {'message': f'{membership.user.username} a été supprimé du foyer.'},
            status=status.HTTP_200_OK
        )
    except IntegrityError:
            return Response(
                        {'error': 'Une erreur est survenue.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            
        
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def promote_member_view(request, membership_id):
    if request.user.membership.role != 'owner':
        return Response(
            {'error': 'Seul le propriétaire peut modifier les rôles.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    membership = get_object_or_404(
        Membership,
        id=membership_id,
        organization=request.user.membership.organization
    )
    
    if membership.user == request.user:
        return Response(
            {'error': 'Vous ne pouvez pas modifier votre propre rôle.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if membership.role == 'member':
        membership.role = 'admin'
        message = f'{membership.user.username} est maintenant administrateur.'
    elif membership.role == 'admin':
        membership.role = 'member'
        message = f'{membership.user.username} est maintenant membre.'
    
    try: 
        membership.save()
        return Response({'message': message}, status=status.HTTP_200_OK)  
    except IntegrityError:
        return Response({'error': 'Une erreur est survenue.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_invite_code_view(request):
    if not hasattr(request.user, 'membership'):
        return Response(
            {'error': 'Vous n\'appartenez à aucune organisation.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.user.membership.role != 'owner':
        return Response(
            {'error': 'Seul le propriétaire peut régénérer le code d\'invitation.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    organization = request.user.membership.organization
    
    try:
        organization.invite_code = generate_invite_code()
        organization.save()
        return Response({'invite_code': organization.invite_code}, status=status.HTTP_200_OK)
    except Exception:
        return Response(
            {'error': 'Une erreur est survenue.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )