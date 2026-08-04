from .models import Bill

def get_export_bills_queryset(request):
    bills = Bill.objects.filter(organization=request.organization)
    type_filter = request.GET.get('type')
    year_filter = request.GET.get('year')

    if type_filter in ['SONABEL', 'ONEA']:
        bills = bills.filter(type=type_filter)

    if year_filter:
        bills = bills.filter(period__year=year_filter)

    return bills.order_by('-period', '-id')