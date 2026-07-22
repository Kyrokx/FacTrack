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

    sonabel_bills = bills.filter(type='SONABEL').order_by('period')
    sonabal_consumption = sonabel_bills.values_list('total_consumption', flat=True)
    sonabel_bills_period = sonabel_bills.values_list('period', flat=True)
    periods = [d.strftime("%m/%Y") for d in sonabel_bills_period]
    consumptions = list(sonabal_consumption)

    context = {
        'bills': bills,
        'all_bills_price': all_bills_price,
        'unpaid_bills': unpaid_bills,
        'unpaid_bills_price': unpaid_bills_price,

        # 'sonabel_bills': sonabel_bills,
        # 'sonabal_consumption': sonabal_consumption,
        # 'sonabel_bills_period': sonabel_bills_period,

        'periods': periods,
        'consumptions': consumptions,   
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
    bills = Bill.objects.all()
    return render(request, 'bill/bills_list.html', {'bills': bills})

@login_required
def toggle_bill(request, id):
    bill = Bill.objects.get(id=id)
    bill.paid = not bill.paid  # ← Bascule True/False
    bill.save()
    return redirect('bills_list')