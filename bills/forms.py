from django import forms

from .models import Bill


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['type', 'period', 'deadline', 'price_total', 'previous_index', 'new_index', 'total_consumption', 'paid']
        widgets = {
                'period': forms.DateInput(attrs={'type': 'date'}),
                'deadline': forms.DateInput(attrs={'type': 'date'}),
            }