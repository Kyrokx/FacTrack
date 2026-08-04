import csv
import datetime
from datetime import date
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .mixins import require_organization
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q, Sum

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .forms import BillForm, RegisterForm, OrganizationForm
from .models import Bill,Membership, Organization, generate_invite_code

from .services import *
from .utils import *


# Create your views here.

def login_view(request):
    return render(request, 'registration/login.html')

def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('setup')
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def setup_view(request):
    if hasattr(request.user, 'membership'):
        messages.info(request, 'Vous appartenez déjà à une organisation.')
        return redirect('home')

    return render(request, 'registration/setup.html')

@login_required
def create_organization_view(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            Membership.objects.create(
                user=request.user,
                organization=organization,
                role='owner'
            )
            messages.success(request, 'Foyer crée avec succès !')
            return redirect('home')
    else:
        form = OrganizationForm()
    return render(request, 'registration/create_organization.html', {'form': form})

@login_required
def join_organization_view(request):
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        if hasattr(request.user, 'membership'):
            messages.error(request, 'Vous appartenez déjà à une organisation.')
            return redirect('home')
        try:
            organization = Organization.objects.get(invite_code=invite_code)
            Membership.objects.create(
                user=request.user,
                organization=organization,
                role='member'
            )
            messages.success(request, f'Vous avez rejoint le foyer {organization.name} avec succès !')
            return redirect('home')
        except Organization.DoesNotExist:
            messages.error(request, 'Code d\'invitation invalide.')
    return render(request, 'registration/join_organization.html')

@require_organization
def home_view(request):
    selected_year = request.GET.get('year', None)
    available_years = list(Bill.objects.dates('period', 'year', order='DESC'))

    bills = Bill.objects.filter(organization=request.organization)
    if selected_year:
        bills = bills.filter(period__year=selected_year)

    current_year = datetime.date.today().year
    previous_year = current_year - 1

    bills_stats = get_bill_stats(bills)
    sonabel_stats = get_sonabel_stats(bills)
    onea_stats = get_onea_stats(bills)
    price_chart = get_price_chart_data(bills)
    year_comparison = get_year_comparison(bills, current_year, previous_year)

    context = {
        'bills': bills,
        'selected_year': selected_year,
        'available_years': available_years,
        'current_year': current_year,
        'previous_year': previous_year,

        **bills_stats,

        'sonabel_bills_descending': sonabel_stats['bills_descending'],
        'all_sonabel_bills_price': sonabel_stats['total_price'],
        'average_sonabel_consumption': sonabel_stats['avg_consumption'],
        'average_sonabel_price': sonabel_stats['avg_price'],
        'sonabel_consumption_percentage': sonabel_stats['consumption_pct'],
        'sonabel_price_percentage': sonabel_stats['price_pct'],
        'periods_1': sonabel_stats['periods'],
        'consumptions_1': sonabel_stats['consumptions'],

        'onea_bills_descending': onea_stats['bills_descending'],
        'all_onea_bills_price': onea_stats['total_price'],
        'average_onea_consumption': onea_stats['avg_consumption'],
        'average_onea_price': onea_stats['avg_price'],
        'onea_consumption_percentage': onea_stats['consumption_pct'],
        'onea_price_percentage': onea_stats['price_pct'],
        'periods_2': onea_stats['periods'],
        'consumptions_2': onea_stats['consumptions'],

        **price_chart,
        **year_comparison,
    }
    return render(request, 'bill/index.html', context)


@require_organization
def organization_settings_view(request):
    if request.user.membership.role not in ['owner', 'admin']:
            messages.error(request, 'Accès réservé aux administrateurs.')
            return redirect('home')
    organization = request.organization
    members = organization.memberships.all()

    if request.method == 'POST' and 'regenerate_code' in request.POST:
        organization.invite_code = generate_invite_code()
        organization.save()
        messages.success(request, 'Code d\'invitation régénéré avec succès !')
        return redirect('organization_settings')
    context = {
        'organization': organization,
        'members': members,
    }
    return render(request, 'bill/organization_settings.html', context)

@require_organization
def promote_member_view(request, membership_id):
    if request.method != 'POST':
        return redirect('organization_settings')
    
    if request.user.membership.role != 'owner':
        messages.error(request, 'Seul le propriétaire peut modifier les rôles.')
        return redirect('organization_settings')
    
    membership = get_object_or_404(
        Membership, 
        id=membership_id, 
        organization=request.organization
    )
    
    if membership.user == request.user:
        messages.error(request, 'Vous ne pouvez pas modifier votre propre rôle.')
        return redirect('organization_settings')
    
    if membership.role == 'member':
        membership.role = 'admin'
        messages.success(request, f'{membership.user.username} est maintenant administrateur.')
    elif membership.role == 'admin':
        membership.role = 'member'
        messages.success(request, f'{membership.user.username} est maintenant membre.')
    
    membership.save()
    return redirect('organization_settings')

@require_organization
def remove_member_view(request, membership_id):
    if request.method != 'POST':
        return redirect('organization_settings')
    
    if request.user.membership.role != 'owner':
        messages.error(request, 'Seul le propriétaire peut supprimer des membres.')
        return redirect('organization_settings')
    
    membership = get_object_or_404(
        Membership, 
        id=membership_id, 
        organization=request.organization
    )
    
    if membership.user == request.user:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('organization_settings')

    if membership.role == 'owner':
        messages.error(request, 'Vous ne pouvez pas supprimer un propriétaire.')
        return redirect('organization_settings')

    membership.delete()
    messages.success(request, f'{membership.user.username} a été supprimé du foyer.')
    return redirect('organization_settings')

@require_organization
def leave_organization_view(request):
    if request.method != 'POST':
        return redirect('organization_settings')
    
    membership = get_object_or_404(
        Membership, 
        user=request.user, 
        organization=request.organization
    )
    
    if membership.role == 'owner':
        messages.error(request, 'Le propriétaire ne peut pas quitter le foyer. Veuillez transférer la propriété ou supprimer le foyer.')
        return redirect('organization_settings')

    membership.delete()
    messages.success(request, 'Vous avez quitté le foyer avec succès.')
    return redirect('setup')

@require_organization
def add_bills(request):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.organization = request.organization
            bill.save() 
            messages.success(request, 'Facture ajoutée avec succès !')
            return redirect('home')
    else:
        form = BillForm()
    return render(request, 'bill/add_bills.html', {'form': form})

@require_organization
def edit_bill(request, id):
    bill = get_object_or_404(Bill, id=id, organization=request.organization)

    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facture modifiée avec succès !')
            return redirect('bills_list')
    else:
        form = BillForm(instance=bill)

    return render(request, 'bill/edit_bill.html', {'form': form, 'bill': bill})


@require_organization
def bill_detail(request, id):
    bill = get_object_or_404(Bill, id=id, organization=request.organization)
    today = date.today()
    days_until_deadline = (bill.deadline - today).days if bill.deadline else 0
    consumption_diff = bill.new_index - bill.previous_index

    context = {
        'bill': bill,
        'unit': 'kWh' if bill.type == 'SONABEL' else 'm³',
        'days_until_deadline': days_until_deadline,
        'is_overdue': bool(bill.deadline and bill.deadline < today and not bill.paid),
        'consumption_diff': consumption_diff,
    }
    return render(request, 'bill/bill_detail.html', context)


@require_organization
def delete_bill(request, id):
    bill = get_object_or_404(Bill, id=id,organization=request.organization)

    if request.method != 'POST':
        return redirect('bills_list')

    bill.delete()
    messages.success(request, 'Facture supprimée avec succès !')
    return redirect('bills_list')



@require_organization
def export_bills_csv(request):
    bills = get_export_bills_queryset(request)
    return generate_bills_csv(bills)

@require_organization
def export_bills_pdf(request):
    bills = list(get_export_bills_queryset(request))
    export_date = datetime.date.today().strftime('%Y-%m-%d')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factrack_factures_{export_date}.pdf"'
    response.write(generate_bills_pdf(bills))
    return response


@require_organization
def bills_list(request):
    bills = Bill.objects.filter(organization=request.organization)
    bills, type_filter, q, sort_field, order = get_filtered_bills(request, bills)

    paginator = Paginator(bills, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'bill/bills_list.html', {
        'bills': page_obj,
        'page_obj': page_obj,
        'active_filter': type_filter,
        'q': q,
        'current_sort': sort_field,
        'current_order': order,
    })


@require_organization
def toggle_bill(request, id):
    if request.method != 'POST':
        return redirect('bills_list')

    bill = bill = get_object_or_404(Bill, id=id, organization=request.organization)
    bill.paid = not bill.paid
    bill.save()
    messages.success(request, 'Statut de la facture mis à jour !')
    return redirect('bills_list')