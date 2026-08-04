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


def _get_export_bills_queryset(request):
    bills = Bill.objects.filter(organization=request.organization)
    type_filter = request.GET.get('type')
    year_filter = request.GET.get('year')

    if type_filter in ['SONABEL', 'ONEA']:
        bills = bills.filter(type=type_filter)

    if year_filter:
        bills = bills.filter(period__year=year_filter)

    return bills.order_by('-period', '-id')


@require_organization
def export_bills_csv(request):
    bills = _get_export_bills_queryset(request)
    export_date = datetime.date.today().strftime('%Y-%m-%d')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="factrack_factures_{export_date}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Type',
        'Periode',
        'Date limite',
        'Prix total (FCFA)',
        'Ancien index',
        'Nouvel index',
        'Consommation',
        'Statut',
    ])

    for bill in bills:
        writer.writerow([
            bill.id,
            bill.type,
            bill.period.strftime('%m/%Y') if bill.period else '',
            bill.deadline.strftime('%d/%m/%Y') if bill.deadline else '',
            bill.price_total,
            bill.previous_index,
            bill.new_index,
            bill.total_consumption,
            'Payée' if bill.paid else 'Impayée',
        ])

    return response


@require_organization
def export_bills_pdf(request):
    bills = list(_get_export_bills_queryset(request))
    export_date = datetime.date.today().strftime('%Y-%m-%d')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factrack_factures_{export_date}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='FacTrackTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1E3A5F'),
        alignment=TA_LEFT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='FacTrackSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#718096'),
        alignment=TA_LEFT,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='FacTrackCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1A202C'),
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='FacTrackEmpty',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#E74C3C'),
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=12,
    ))

    elements = []
    elements.append(Paragraph('FacTrack', styles['FacTrackTitle']))
    elements.append(Paragraph('Liste des factures', styles['FacTrackSubtitle']))
    elements.append(Paragraph(f'Généré le {datetime.date.today().strftime("%d/%m/%Y")}', styles['FacTrackSubtitle']))
    elements.append(Spacer(1, 10))

    total_amount = sum(float(bill.price_total or 0) for bill in bills)
    paid_count = sum(1 for bill in bills if bill.paid)
    unpaid_count = len(bills) - paid_count

    summary_data = [[
        Paragraph('<b>Total factures</b><br/>{}'.format(len(bills)), styles['FacTrackCenter']),
        Paragraph('<b>Montant total</b><br/>{:,.0f} FCFA'.format(total_amount).replace(',', ' '), styles['FacTrackCenter']),
        Paragraph('<b>Payées</b><br/>{}'.format(paid_count), styles['FacTrackCenter']),
        Paragraph('<b>Impayées</b><br/>{}'.format(unpaid_count), styles['FacTrackCenter']),
    ]]
    summary_table = Table(summary_data, colWidths=[60 * mm, 70 * mm, 45 * mm, 45 * mm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F4F8')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    def _bill_type_color(bill):
        return colors.HexColor('#2E86AB') if bill.type == 'SONABEL' else colors.HexColor('#20B2AA')

    def _footer(canvas, doc_obj):
        canvas.saveState()
        footer_text = f'FacTrack © - Exporté le {datetime.date.today().strftime("%d/%m/%Y")}'
        page_text = f'Page {canvas.getPageNumber()}'
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#718096'))
        canvas.drawString(doc_obj.leftMargin, 10 * mm, footer_text)
        canvas.drawRightString(doc_obj.pagesize[0] - doc_obj.rightMargin, 10 * mm, page_text)
        canvas.restoreState()

    if bills:
        table_data = [[
            Paragraph('<b>Type</b>', styles['FacTrackCenter']),
            Paragraph('<b>Période</b>', styles['FacTrackCenter']),
            Paragraph('<b>Date limite</b>', styles['FacTrackCenter']),
            Paragraph('<b>Prix total</b>', styles['FacTrackCenter']),
            Paragraph('<b>Ancien index</b>', styles['FacTrackCenter']),
            Paragraph('<b>Nouveau index</b>', styles['FacTrackCenter']),
            Paragraph('<b>Consommation</b>', styles['FacTrackCenter']),
            Paragraph('<b>Statut</b>', styles['FacTrackCenter']),
        ]]

        for bill in bills:
            table_data.append([
                Paragraph(bill.type, styles['FacTrackCenter']),
                Paragraph(bill.period.strftime('%m/%Y') if bill.period else '', styles['FacTrackCenter']),
                Paragraph(bill.deadline.strftime('%d/%m/%Y') if bill.deadline else '', styles['FacTrackCenter']),
                Paragraph(f'{bill.price_total} FCFA', styles['FacTrackCenter']),
                Paragraph(str(bill.previous_index), styles['FacTrackCenter']),
                Paragraph(str(bill.new_index), styles['FacTrackCenter']),
                Paragraph(str(bill.total_consumption), styles['FacTrackCenter']),
                Paragraph(
                    '<font color="#27AE60">Payée</font>' if bill.paid else '<font color="#E74C3C">Impayée</font>',
                    styles['FacTrackCenter']
                ),
            ])

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[22 * mm, 22 * mm, 28 * mm, 28 * mm, 22 * mm, 22 * mm, 24 * mm, 22 * mm],
        )

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])

        for index, bill in enumerate(bills, start=1):
            row = index
            row_color = colors.white if index % 2 else colors.HexColor('#F0F4F8')
            table_style.add('BACKGROUND', (0, row), (-1, row), row_color)
            table_style.add('LINEBEFORE', (0, row), (0, row), 3, _bill_type_color(bill))
            status_color = colors.HexColor('#27AE60') if bill.paid else colors.HexColor('#E74C3C')
            table_style.add('TEXTCOLOR', (7, row), (7, row), status_color)

        table.setStyle(table_style)
        elements.append(table)
    else:
        elements.append(Paragraph('Aucune facture trouvée', styles['FacTrackEmpty']))

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


@require_organization
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

    bills = Bill.objects.filter(organization=request.organization)
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


@require_organization
def toggle_bill(request, id):
    if request.method != 'POST':
        return redirect('bills_list')

    bill = bill = get_object_or_404(Bill, id=id, organization=request.organization)
    bill.paid = not bill.paid
    bill.save()
    messages.success(request, 'Statut de la facture mis à jour !')
    return redirect('bills_list')