from django import forms
from .models import Property, Unit
from accounts.models import Tenant  # ⚠️ Importa o Tenant!

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

    def __init__(self, *args, **kwargs):
        landlord = kwargs.pop('landlord', None)
        super(UnitForm, self).__init__(*args, **kwargs)

        if landlord:
            self.fields['tenant'].queryset = Tenant.objects.filter(landlord=landlord)
        else:
            self.fields['tenant'].queryset = Tenant.objects.none()