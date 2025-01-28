from django import forms
from accounts.models import Landlord, Tenant
from properties.models import Property, Unit
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class LandlordForm(forms.ModelForm):
    # Campos do modelo CustomUser
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    cpf = forms.CharField(max_length=14, required=True)

    class Meta:
        model = Landlord
        fields = ["marital_status", "profession"]  # Campos específicos do Landlord

    def __init__(self, *args, **kwargs):
        # Inicializar com dados do CustomUser
        user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if user_instance:
            self.fields['first_name'].initial = user_instance.first_name
            self.fields['last_name'].initial = user_instance.last_name
            self.fields['cpf'].initial = user_instance.cpf
            
    def save(self, commit=True):
        # Salvar os dados do Landlord e do CustomUser
        landlord_instance = super().save(commit=False)
        user_instance = landlord_instance.user
        user_instance.first_name = self.cleaned_data['first_name']
        user_instance.last_name = self.cleaned_data['last_name']
        user_instance.cpf = self.cleaned_data['cpf']
        if commit:
            user_instance.save()
            landlord_instance.save()
        return landlord_instance


class TenantForm(forms.ModelForm):
    # Campos do modelo CustomUser
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    cpf = forms.CharField(max_length=14, required=True)
    
    class Meta:
        model = Tenant
        fields = ["marital_status", "profession"]  # Campos específicos do Tenant

    def __init__(self, *args, **kwargs):
        # Inicializar com dados do CustomUser
        user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if user_instance:
            self.fields['first_name'].initial = user_instance.first_name
            self.fields['last_name'].initial = user_instance.last_name
            self.fields['cpf'].initial = user_instance.cpf
            
    def save(self, commit=True):
        # Salvar os dados do Tenant e do CustomUser
        tenant_instance = super().save(commit=False)
        user_instance = tenant_instance.user
        user_instance.first_name = self.cleaned_data['first_name']
        user_instance.last_name = self.cleaned_data['last_name']
        user_instance.cpf = self.cleaned_data['cpf']
        
        if commit:
            user_instance.save()
            tenant_instance.save()
        return tenant_instance

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ["name", "street", "number", "complement", "city", "state", "zip_code"]

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["unit_number", "status", "monthly_rent", "deposit_amount", "move_in_date", "move_out_date"]
