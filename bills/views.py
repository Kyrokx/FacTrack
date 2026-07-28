from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
import datetime

from .forms import BillForm
from .models import Bill


# Create your views here.

def login_view(request):
    return render(request, 'registration/login.html')


@login_required
def home_view(request):
    selected_year = request.GET.get('year', None)
    available_years = list(Bill.objects.dates('period', 'year', order='DESC'))

    bills = Bill.objects.all()
    if selected_year:
        bills = bills.filter(period__year=selected_year)

    all_bills_price = bills.aggregate(Sum('price_total'))['price_total__sum'] or 0
    unpaid_bills = bills.filter(paid=False).all()
    unpaid_bills_price = unpaid_bills.aggregate(Sum('price_total'))['price_total__sum'] or 0

    sonabel_bills_descending = bills.filter(type='SONABEL').order_by('-period')[:5]
    sonabel_bills = bills.filter(type='SONABEL').order_by('period')

    all_sonabel_bills_price = bills.filter(type="SONABEL").aggregate(Sum('price_total'))['price_total__sum'] or 0

    sonabal_consumption = sonabel_bills.values_list('total_consumption', flat=True)
    sonabel_bills_period = sonabel_bills.values_list('period', flat=True)
    average_sonabel_consumption = sum(sonabal_consumption) / len(sonabal_consumption) if sonabal_consumption else 0

    # percentage sonabel consumption compared to the previous month
    sonabel_consumptions_list = list(sonabal_consumption)
    sonabel_consumption_percentage = 0
    if len(sonabel_consumptions_list) >= 2:
        last = sonabel_consumptions_list[-1]
        prev = sonabel_consumptions_list[-2]
        if prev:
            sonabel_consumption_percentage = ((last - prev) / prev) * 100

    average_sonabel_price = sum(bill.price_total for bill in sonabel_bills) / len(sonabel_bills) if sonabel_bills else 0
    # percentage sonabel price compared to the previous month
    sonabel_prices = sonabel_bills.values_list('price_total', flat=True)
    sonabel_prices_list = list(sonabel_prices)
    sonabel_price_percentage = 0
    if len(sonabel_prices_list) >= 2:
        last_price = sonabel_prices_list[-1]
        prev_price = sonabel_prices_list[-2]
        if prev_price:
            sonabel_price_percentage = ((last_price - prev_price) / prev_price) * 100

    periods_1 = [d.strftime("%m/%Y") for d in sonabel_bills_period]
    consumptions_1 = sonabel_consumptions_list

    onea_bills_descending = bills.filter(type='ONEA').order_by('-period')[:5]
    onea_bills = bills.filter(type='ONEA').order_by('period')

    all_onea_bills_price = bills.filter(type="ONEA").aggregate(Sum('price_total'))['price_total__sum'] or 0

    onea_consumption = onea_bills.values_list('total_consumption', flat=True)
    onea_bills_period = onea_bills.values_list('period', flat=True)
    average_onea_consumption = sum(onea_consumption) / len(onea_consumption) if onea_consumption else 0
    average_onea_price = sum(bill.price_total for bill in onea_bills) / len(onea_bills) if onea_bills else 0
    # percentage onea consumption compared to the previous month
    onea_consumptions_list = list(sonabal_consumption)
    onea_consumption_percentage = 0
    if len(onea_consumptions_list) >= 2:
        last = onea_consumptions_list[-1]
        prev = onea_consumptions_list[-2]
        if prev:
            onea_consumption_percentage = ((last - prev) / prev) * 100

    average_onea_price = sum(bill.price_total for bill in onea_bills) / len(onea_bills) if onea_bills else 0
    # percentage onea price compared to the previous month
    onea_prices = onea_bills.values_list('price_total', flat=True)
    onea_prices_list = list(onea_prices)
    onea_price_percentage = 0
    if len(onea_prices_list) >= 2:
        last_price = onea_prices_list[-1]
        prev_price = onea_prices_list[-2]
        if prev_price:
            onea_price_percentage = ((last_price - prev_price) / prev_price) * 100
    periods_2 = [d.strftime("%m/%Y") for d in onea_bills_period]
    consumptions_2 = list(onea_consumption)

    sonabel_price_rows = bills.filter(type='SONABEL').values('period').annotate(total=Sum('price_total')).order_by('period')
    onea_price_rows = bills.filter(type='ONEA').values('period').annotate(total=Sum('price_total')).order_by('period')
    sonabel_price_map = {row['period']: float(row['total'] or 0) for row in sonabel_price_rows}
    onea_price_map = {row['period']: float(row['total'] or 0) for row in onea_price_rows}
    all_price_periods = sorted(set(sonabel_price_map.keys()) | set(onea_price_map.keys()))
    price_periods = [d.strftime("%m/%Y") for d in all_price_periods]
    sonabel_prices = [sonabel_price_map.get(period, 0.0) for period in all_price_periods]
    onea_prices = [onea_price_map.get(period, 0.0) for period in all_price_periods]

    paid_count = bills.filter(paid=True).count()
    unpaid_count = bills.filter(paid=False).count()

    current_year = datetime.date.today().year
    previous_year = current_year - 1
    month_labels = [f"{month:02d}" for month in range(1, 13)]
    current_year_monthly = []
    previous_year_monthly = []
    current_year_bills = Bill.objects.filter(period__year=current_year)
    previous_year_bills = Bill.objects.filter(period__year=previous_year)
    for month in range(1, 13):
        current_total = current_year_bills.filter(period__month=month).aggregate(total=Sum('price_total'))['total'] or 0
        previous_total = previous_year_bills.filter(period__month=month).aggregate(total=Sum('price_total'))['total'] or 0
        current_year_monthly.append(float(current_total))
        previous_year_monthly.append(float(previous_total))

    context = {
        'bills': bills,
        'all_bills_price': all_bills_price,
        'unpaid_bills': unpaid_bills,
        'unpaid_bills_price': unpaid_bills_price,

        'sonabel_bills_descending': sonabel_bills_descending,
        'onea_bills_descending': onea_bills_descending,

        'all_sonabel_bills_price': all_sonabel_bills_price,
        'all_onea_bills_price': all_onea_bills_price,

        'average_sonabel_consumption': average_sonabel_consumption,
        'average_sonabel_price': average_sonabel_price,
        'sonabel_consumption_percentage': sonabel_consumption_percentage,
        'sonabel_price_percentage': sonabel_price_percentage,

        'average_onea_consumption': round(average_onea_consumption),
        'average_onea_price': round(average_onea_price),
        'onea_consumption_percentage': round(onea_consumption_percentage),
        'onea_price_percentage': round(onea_price_percentage),

        'periods_1': periods_1,
        'consumptions_1': consumptions_1,

        'periods_2': periods_2,
        'consumptions_2': consumptions_2,
        'selected_year': selected_year,
        'available_years': available_years,
        'sonabel_prices': sonabel_prices,
        'onea_prices': onea_prices,
        'price_periods': price_periods,
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'current_year': current_year,
        'previous_year': previous_year,
        'current_year_monthly': current_year_monthly,
        'previous_year_monthly': previous_year_monthly,
        'month_labels': month_labels,
    }
    return render(request, 'bill/index.html', context)


@login_required
def add_bills(request):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facture ajoutée avec succès !')
            return redirect('home')
    else:
        form = BillForm()
    return render(request, 'bill/add_bills.html', {'form': form})


@login_required
def edit_bill(request, id):
    bill = get_object_or_404(Bill, id=id)

    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facture modifiée avec succès !')
            return redirect('bills_list')
    else:
        form = BillForm(instance=bill)

    return render(request, 'bill/edit_bill.html', {'form': form, 'bill': bill})


@login_required
def delete_bill(request, id):
    bill = get_object_or_404(Bill, id=id)

    if request.method != 'POST':
        return redirect('bills_list')

    bill.delete()
    messages.success(request, 'Facture supprimée avec succès !')
    return redirect('bills_list')


@login_required
def bills_list(request):
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

    order_prefix = '-' if order == 'desc' else ''

    bills = Bill.objects.all()
    if type_filter in ['SONABEL', 'ONEA']:
        bills = bills.filter(type=type_filter)

    if q:
        bills = bills.filter(
            Q(period__icontains=q) |
            Q(type__icontains=q) |
            Q(price_total__icontains=q)
        )

    bills = bills.order_by(f'{order_prefix}{sort_field}')

    paginator = Paginator(bills, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'bill/bills_list.html',
        {
            'bills': page_obj,
            'page_obj': page_obj,
            'active_filter': type_filter,
            'q': q,
            'current_sort': sort_field,
            'current_order': order,
        }
    )


@login_required
def toggle_bill(request, id):
    if request.method != 'POST':
        return redirect('bills_list')

    bill = get_object_or_404(Bill, id=id)
    bill.paid = not bill.paid
    bill.save()
    messages.success(request, 'Statut de la facture mis à jour !')
    return redirect('bills_list')
