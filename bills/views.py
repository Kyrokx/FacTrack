from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Bill
from django.db.models import Sum
from .forms import BillForm


# Create your views here.

def login_view(request):
    return render(request, 'registration/login.html')
@login_required
def home_view(request):
    bills = Bill.objects.all()
    all_bills_price = Bill.objects.aggregate(Sum('price_total'))['price_total__sum'] or 0
    unpaid_bills = Bill.objects.filter(paid=False).all()
    unpaid_bills_price = unpaid_bills.aggregate(Sum('price_total'))['price_total__sum'] or 0

    sonabel_bills_descending = bills.filter(type='SONABEL').order_by('-period')[:5]
    sonabel_bills = bills.filter(type='SONABEL').order_by('period')

    all_sonabel_bills_price = Bill.objects.filter(type="SONABEL").aggregate(Sum('price_total'))['price_total__sum'] or 0

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

    all_onea_bills_price = Bill.objects.filter(type="ONEA").aggregate(Sum('price_total'))['price_total__sum'] or 0

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
        # 'sonabal_consumption': sonabal_consumption,
        # 'sonabel_bills_period': sonabel_bills_period,

        'periods_1': periods_1,
        'consumptions_1': consumptions_1,   

        'periods_2': periods_2,
        'consumptions_2': consumptions_2,  
    }
    return render(request, 'bill/index.html', context)

@login_required
def add_bills(request):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = BillForm()
    return render(request, 'bill/add_bills.html', {'form': form})

@login_required
def bills_list(request):
    type_filter = request.GET.get('type')  # récupère ?type=SONABEL ou ?type=ONEA
    bills = Bill.objects.all()
    if type_filter in ['SONABEL', 'ONEA']:
        bills = bills.filter(type=type_filter)
    return render(request, 'bill/bills_list.html', {'bills': bills, 'active_filter': type_filter})

@login_required
def toggle_bill(request, id):
    bill = Bill.objects.get(id=id)
    bill.paid = not bill.paid  # ← Bascule True/False
    bill.save()
    return redirect('bills_list')