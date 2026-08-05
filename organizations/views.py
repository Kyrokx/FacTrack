from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .mixins import require_organization
from django.contrib import messages

from .forms import OrganizationForm
from .models import Membership, Organization, generate_invite_code

# Create your views here.


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