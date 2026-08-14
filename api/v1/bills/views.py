from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from bills.models import Bill
from .serializers import BillSerializer

from bills.services import get_bill_stats, get_sonabel_stats, get_onea_stats, get_price_chart_data
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from bills.utils import get_export_bills_queryset, generate_bills_pdf
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_list_view(request):
    if not hasattr(request.user, 'membership'):
        return Response(
            {'error': 'Vous n\'appartenez à aucune organisation.'},
            status=status.HTTP_404_NOT_FOUND
        )
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
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    if not hasattr(request.user, 'membership'):
        return Response({'error': 'Aucune organisation.'}, status=status.HTTP_404_NOT_FOUND)

    org = request.user.membership.organization
    bills = Bill.objects.filter(organization=org)

    year = request.query_params.get('year')
    if year:
        bills = bills.filter(period__year=year)


    stats = get_bill_stats(bills)
    sonabel = get_sonabel_stats(bills)
    onea = get_onea_stats(bills)
    chart = get_price_chart_data(bills)

    return Response({
        # Stats globales
        'total_amount': stats['all_bills_price'],
        'unpaid_count': stats['unpaid_count'],
        'unpaid_total': stats['unpaid_bills_price'],
        'paid_count': stats['paid_count'],
        'total_count': stats['total_bills_count'],

        # SONABEL
        'sonabel_total': sonabel['total_price'],
        'sonabel_avg_consumption': sonabel['avg_consumption'],
        'sonabel_consumption_pct': sonabel['consumption_pct'],
        'sonabel_avg_price': sonabel['avg_price'],
        'sonabel_price_pct': sonabel['price_pct'],
        'sonabel_periods': sonabel['periods'],
        'sonabel_consumptions': sonabel['consumptions'],
        'sonabel_prices': sonabel['prices'],
        'last_sonabel': BillSerializer(sonabel['bills_descending'], many=True).data,

        # ONEA
        'onea_total': onea['total_price'],
        'onea_avg_consumption': onea['avg_consumption'],
        'onea_consumption_pct': onea['consumption_pct'],
        'onea_avg_price': onea['avg_price'],
        'onea_price_pct': onea['price_pct'],
        'onea_periods': onea['periods'],
        'onea_consumptions': onea['consumptions'],
        'onea_prices': onea['prices'],
        'last_onea': BillSerializer(onea['bills_descending'], many=True).data,

        # Graphique dépenses
        'price_periods': chart['price_periods'],
        'sonabel_price_chart': chart['sonabel_prices'],
        'onea_price_chart': chart['onea_prices'],
    })
    
    
class BillsPDFExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = request.user.membership.organization
        bills = Bill.objects.filter(organization=organization)
        
        type_filter = request.GET.get('type')
        year_filter = request.GET.get('year')

        if type_filter in ['SONABEL', 'ONEA']:
            bills = bills.filter(type=type_filter)
        if year_filter:
            bills = bills.filter(period__year=year_filter)

        bills = bills.order_by('-period', '-id')
        
        pdf = generate_bills_pdf(list(bills))
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="factrack_factures.pdf"'
        return response