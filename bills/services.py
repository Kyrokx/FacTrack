import datetime
from django.db.models import Sum
from django.db.models import Q

def get_bill_stats(bills):
    unpaid_bills = bills.filter(paid=False)
    return {
        'all_bills_price': bills.aggregate(Sum('price_total'))['price_total__sum'] or 0,
        'unpaid_bills': unpaid_bills,
        'unpaid_bills_price': unpaid_bills.aggregate(Sum('price_total'))['price_total__sum'] or 0,
        'unpaid_count': unpaid_bills.count(),
        'paid_count': bills.filter(paid=True).count(),
        'total_bills_count': bills.count(),
    }


def _get_type_stats(bills, bill_type):
    """Helper générique pour SONABEL et ONEA — évite la duplication de code."""
    type_bills = bills.filter(type=bill_type).order_by('period')
    type_bills_descending = bills.filter(type=bill_type).order_by('-period')[:5]
    total_price = bills.filter(type=bill_type).aggregate(Sum('price_total'))['price_total__sum'] or 0

    consumptions = list(type_bills.values_list('total_consumption', flat=True))
    periods = list(type_bills.values_list('period', flat=True))
    prices = list(type_bills.values_list('price_total', flat=True))

    avg_consumption = sum(consumptions) / len(consumptions) if consumptions else 0
    avg_price = sum(float(p) for p in prices) / len(prices) if prices else 0

    consumption_pct = 0
    if len(consumptions) >= 2 and consumptions[-2]:
        consumption_pct = ((consumptions[-1] - consumptions[-2]) / consumptions[-2]) * 100

    price_pct = 0
    if len(prices) >= 2 and prices[-2]:
        price_pct = ((float(prices[-1]) - float(prices[-2])) / float(prices[-2])) * 100

    return {
        'total_price': total_price,
        'bills_descending': type_bills_descending,
        'avg_consumption': round(avg_consumption),
        'consumption_pct': round(consumption_pct),
        'avg_price': round(avg_price),
        'price_pct': round(price_pct),
        'periods': [d.strftime("%m/%Y") for d in periods],
        'consumptions': consumptions,
        'prices': [float(p) for p in prices],
    }


def get_sonabel_stats(bills):
    return _get_type_stats(bills, 'SONABEL')


def get_onea_stats(bills):
    return _get_type_stats(bills, 'ONEA')


def get_price_chart_data(bills):
    sonabel_rows = bills.filter(type='SONABEL').values('period').annotate(total=Sum('price_total')).order_by('period')
    onea_rows = bills.filter(type='ONEA').values('period').annotate(total=Sum('price_total')).order_by('period')

    sonabel_map = {row['period']: float(row['total'] or 0) for row in sonabel_rows}
    onea_map = {row['period']: float(row['total'] or 0) for row in onea_rows}
    all_periods = sorted(set(sonabel_map.keys()) | set(onea_map.keys()))

    return {
        'price_periods': [d.strftime("%m/%Y") for d in all_periods],
        'sonabel_prices': [sonabel_map.get(p, 0.0) for p in all_periods],
        'onea_prices': [onea_map.get(p, 0.0) for p in all_periods],
    }


def get_year_comparison(bills, current_year, previous_year):
    
    current_bills = bills.filter(period__year=current_year)
    previous_bills = bills.filter(period__year=previous_year)

    current_monthly = []
    previous_monthly = []
    for month in range(1, 13):
        current_total = current_bills.filter(period__month=month).aggregate(total=Sum('price_total'))['total'] or 0
        previous_total = previous_bills.filter(period__month=month).aggregate(total=Sum('price_total'))['total'] or 0
        current_monthly.append(float(current_total))
        previous_monthly.append(float(previous_total))

    return {
        'current_year_monthly': current_monthly,
        'previous_year_monthly': previous_monthly,
        'month_labels': [f"{m:02d}" for m in range(1, 13)],
    }


def get_filtered_bills(request, bills):
    type_filter = request.GET.get('type')
    q = request.GET.get('q', '')
    sort_param = request.GET.get('sort', '-period')
    order = request.GET.get('order', 'desc')

    allowed_sort_fields = {'period', 'deadline', 'price_total', 'total_consumption', 'paid'}
    sort_field = sort_param.lstrip('-')
    if sort_field not in allowed_sort_fields:
        sort_field = 'period'

    if order not in {'asc', 'desc'}:
        order = 'desc' if sort_param.startswith('-') else 'asc'

    if type_filter in ['SONABEL', 'ONEA']:
        bills = bills.filter(type=type_filter)

    if q:
        bills = bills.filter(
            Q(type__icontains=q) |
            Q(price_total__icontains=q)
        )

    order_prefix = '-' if order == 'desc' else ''
    bills = bills.order_by(f'{order_prefix}{sort_field}')

    return bills, type_filter, q, sort_field, order