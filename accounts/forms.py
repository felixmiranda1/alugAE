from allauth.account.forms import LoginForm
from django import forms
from .models import CustomUser, Landlord

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

    class Meta:
        model = CustomUser
        fields = ['cpf']

    def save(self, user, commit=True):
        # Update CustomUser and Landlord data
        user.cpf = self.cleaned_data.get("cpf")
        landlord = Landlord.objects.get(user=user)
        landlord.marital_status = self.cleaned_data.get("marital_status")
        landlord.profession = self.cleaned_data.get("profession")
        if commit:
            user.save()
            landlord.save()
        return landlord
