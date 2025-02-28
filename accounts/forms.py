from allauth.account.forms import LoginForm
from django import forms
from .models import CustomUser, Landlord, Tenant, AdoptionCode
from datetime import timedelta
from django.utils.timezone import now

# Custom Login Form
class CustomLoginForm(LoginForm):
    email_or_phone = forms.CharField(label="Email or Phone", max_length=255)

    def clean(self):
        # Overriding the clean method to support email or phone login
        email_or_phone = self.cleaned_data.get("email_or_phone")
        password = self.cleaned_data.get("password")
        if "@" in email_or_phone:
            self.cleaned_data["email"] = email_or_phone
        else:
            self.cleaned_data["email"] = None
            self.cleaned_data["phone"] = email_or_phone
        return super().clean()

# Form for essential user data (First step of landlord registration)
class EssentialLandlordForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'password', 'first_name', 'last_name']

    def save(self, commit=True):
        # Extract username from the email
        username = self.cleaned_data["email"].split("@")[0]
        
        user = CustomUser.objects.create_user(
            username= username,
            email=self.cleaned_data["email"],
            phone=self.cleaned_data["phone"],
            password=self.cleaned_data["password"]
        )
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


# Form for optional data (Part 2 of the registration process)
class OptionalLandlordForm(forms.ModelForm):
    marital_status = forms.CharField(max_length=20, required=False)
    profession = forms.CharField(max_length=100, required=False)
    cpf = forms.CharField(max_length=14, required=False)
    pix_key = forms.CharField(max_length=100, required=False)

    class Meta:
        model = CustomUser
        fields = ['cpf']

    def save(self, user, commit=True):
        # Update CustomUser and Landlord data
        user.cpf = self.cleaned_data.get("cpf")
        landlord = Landlord.objects.get(user=user)
        landlord.marital_status = self.cleaned_data.get("marital_status")
        landlord.profession = self.cleaned_data.get("profession")
        landlord.pix_key = self.cleaned_data.get("pix_key")
        if commit:
            user.save()
            landlord.save()
        return landlord


class TenantSignupForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    cpf = forms.CharField(max_length=14, required=True)
    marital_status = forms.CharField(max_length=20, required=True)
    profession = forms.CharField(max_length=100, required=True)
    adoption_code = forms.CharField(max_length=8, required=True)  

    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'password', 'first_name', 'last_name', 'cpf']

    def clean_adoption_code(self):
        """ Valida se o código de adoção existe e retorna apenas o ID do Landlord. """
        code = self.cleaned_data.get('adoption_code')
        try:
            landlord_id = AdoptionCode.objects.get(code=code).landlord_id  # Apenas o ID
            return landlord_id
        except AdoptionCode.DoesNotExist:
            raise forms.ValidationError("Código de adoção inválido.")

    def save(self, commit=True):
        """ Salva o usuário e cria o Tenant com o landlord correto. """
        username = self.cleaned_data["email"].split("@")[0]

        user = CustomUser.objects.create_user(
            username=username,
            email=self.cleaned_data["email"],
            phone=self.cleaned_data["phone"],
            password=self.cleaned_data["password"]
        )

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.cpf = self.cleaned_data["cpf"]
        user.save()

        # Obtém o ID do Landlord (apenas ID, sem carregar objeto)
        landlord_id = self.cleaned_data.get('adoption_code')

        # Criar o Tenant com o landlord_id correto
        tenant = Tenant.objects.create(
            user=user,
            marital_status=self.cleaned_data["marital_status"],
            profession=self.cleaned_data["profession"],
            landlord_id=landlord_id  # Agora usamos apenas o ID
        )

        return tenant


        return user, tenant
# Form for updating Landlord profile
class LandlordUpdateForm(forms.ModelForm):
    marital_status = forms.CharField(max_length=20, required=False)  # Optional marital status field
    profession = forms.CharField(max_length=100, required=False)  # Optional profession field
    pix_key = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'cpf']  # Fields allowed for update

    def save(self, user, commit=True):
        # Update CustomUser fields
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.cpf = self.cleaned_data['cpf']
        if commit:
            user.save()

        # Update Landlord-specific fields
        landlord = Landlord.objects.get(user=user)
        landlord.marital_status = self.cleaned_data.get('marital_status')
        landlord.profession = self.cleaned_data.get('profession')
        landlord.pix_key = self.cleaned_data.get('pix_key')
        
        if commit:
            landlord.save()

        return user


# Form for updating Tenant profile
class TenantUpdateForm(forms.ModelForm):
    marital_status = forms.CharField(max_length=20, required=False)  # Optional marital status field
    profession = forms.CharField(max_length=100, required=False)  # Optional profession field

    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'cpf']  # Fields allowed for update

    def save(self, user, commit=True):
        # Update CustomUser fields
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.cpf = self.cleaned_data['cpf']
        if commit:
            user.save()

        # Update Tenant-specific fields
        tenant = Tenant.objects.get(user=user)
        tenant.marital_status = self.cleaned_data.get('marital_status')
        tenant.profession = self.cleaned_data.get('profession')
        if commit:
            tenant.save()

        return user