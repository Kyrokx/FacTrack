from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bills.models import Bill
from .serializers import BillSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_list_view(request):
    bills = Bill.objects.filter(organization=request.user.membership.organization)
    serializer = BillSerializer(bills, many=True)
    return Response(serializer.data)