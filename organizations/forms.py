from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Organization

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
