from django.db import migrations

def link_existing_bills(apps, schema_editor):
    Organization = apps.get_model('organizations', 'Organization')
    Membership = apps.get_model('organizations', 'Membership')
    Bill = apps.get_model('bills', 'Bill')
    User = apps.get_model('auth', 'User')

    # Récupère les bills sans organization
    unlinked_bills = Bill.objects.filter(organization=None)
    
    if not unlinked_bills.exists():
        return  # Rien à faire

    # Crée l'organisation "Maison"
    organization = Organization.objects.create(name='MonRoiFam')

    # Relie tous les bills sans organization à cette org
    unlinked_bills.update(organization=organization)

    # Crée un membership owner pour le superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser and not Membership.objects.filter(user=superuser).exists():
        Membership.objects.create(
            user=superuser,
            organization=organization,
            role='owner'
        )

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('bills', '0008_alter_bill_organization_delete_membership_and_more'),
    ]

    operations = [
        migrations.RunPython(link_existing_bills, migrations.RunPython.noop),
    ]