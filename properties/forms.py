from django import forms
from .models import Property, Unit

# Formulário para propriedades
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'name',
            'street',
            'number',
            'complement',
            'city',
            'state',
            'zip_code',
            'is_standalone',
        ]

# Formulário para unidades
class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            'unit_number',
            'status',
            'tenant',
            'monthly_rent',
            'deposit_amount',
            'move_in_date',
            'move_out_date',
        ]
