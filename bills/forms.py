from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Bill,Organization,Membership


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['type', 'period', 'deadline', 'previous_index', 'new_index', 'total_consumption', 'paid','price_total',]
        widgets = {
                'period': forms.DateInput(attrs={'type': 'date'}),
                'deadline': forms.DateInput(attrs={'type': 'date'}),
            }

        labels = {
            'type': 'Type de facture',
            'period': 'Période de facturation',
            'deadline': 'Date limite de paiement',
            'price_total': 'Montant total',
            'previous_index': 'Index précédent',
            'new_index': 'Nouvel index',
            'total_consumption': 'Consommation totale',
            'paid': 'Payée',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ajoute les classes Tailwind à TOUS les champs
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            })


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
            # Ajoute les classes Tailwind à TOUS les champs
            for field in self.fields.values():
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
                })  

class OrganizationForm(forms.ModelForm):
    class Meta:
            model = Organization
            fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ajoute les classes Tailwind à TOUS les champs
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            })
