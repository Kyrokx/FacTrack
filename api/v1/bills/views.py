from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from bills.models import Bill
from .serializers import BillSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_list_view(request):
    bills = Bill.objects.filter(organization=request.user.membership.organization)
    serializer = BillSerializer(bills, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bill_create_view(request):
    if not hasattr(request.user, 'membership'):
        return Response(
            {'error': 'Vous n\'appartenez à aucune organisation.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BillSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(organization=request.user.membership.organization)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_detail_view(request, id):
    bill = get_object_or_404(Bill, id=id, organization=request.user.membership.organization)
    serializer = BillSerializer(bill)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def bill_update_view(request, id):
    bill = get_object_or_404(Bill, id=id, organization=request.user.membership.organization)
    serializer = BillSerializer(bill, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bill_delete_view(request, id):
    bill = get_object_or_404(Bill, id=id, organization=request.user.membership.organization)
    bill.delete()
    return Response(
        {'message': 'Facture supprimée avec succès.'},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bill_toggle_view(request, id):
    bill = get_object_or_404(Bill, id=id, organization=request.user.membership.organization)
    bill.paid = not bill.paid
    bill.save()
    return Response({
        'message': 'Statut mis à jour.',
        'paid': bill.paid
    })