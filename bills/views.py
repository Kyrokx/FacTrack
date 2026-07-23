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
    periods_1 = [d.strftime("%m/%Y") for d in sonabel_bills_period]
    consumptions_1 = list(sonabal_consumption)


    onea_bills_descending = bills.filter(type='ONEA').order_by('-period')[:5]
    onea_bills = bills.filter(type='ONEA').order_by('period')

    all_onea_bills_price = Bill.objects.filter(type="ONEA").aggregate(Sum('price_total'))['price_total__sum'] or 0

    onea_consumption = onea_bills.values_list('total_consumption', flat=True)
    onea_bills_period = onea_bills.values_list('period', flat=True)
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