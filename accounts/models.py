# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.timezone import now, timedelta
import random
import string
from django.db import models

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        username = extra_fields.get('username', email.split("@")[0])  # Default username from email
        extra_fields.setdefault('username', username)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    def __str__(self):
        return self.email


    class Meta:
        db_table = "user"
        managed = False

# Landlord model 
class Landlord(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="landlord")
    marital_status = models.CharField(max_length=20, blank=True, null=True)  # Optional
    profession = models.CharField(max_length=100, blank=True, null=True)  # Optional
    pix_key = models.CharField(max_length=255, blank=True, null=True)  # Chave PIX do landlord
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Landlord: {self.user.email or self.user.phone}"

    class Meta:
        db_table = "landlord"

# Tenant model
class Tenant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    landlord = models.ForeignKey(
        'accounts.Landlord',  # Substitua por 'CustomUser' se Landlord não for um modelo separado
        on_delete=models.CASCADE,
        related_name="tenants",
        verbose_name="Landlord"
    )  # Relacionamento direto com o Landlord
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tenant: {self.user.email or self.user.phone}"

    class Meta:
        db_table = "tenant"


# Tenant signup code
def default_expiration():
    return now() + timedelta(hours=24)

# Adoption code
def generate_adoption_code():
    """
    Generates a 5-character adoption code: 3 uppercase letters + 2 digits (e.g., ABC12).
    """
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))  # 3 uppercase letters
    numbers = ''.join(random.choices(string.digits, k=2))  # 2 digits
    return letters + numbers  # Example: ABC12

class AdoptionCode(models.Model):
    landlord = models.OneToOneField(
        Landlord,  # Agora referenciamos diretamente a tabela Landlord
        on_delete=models.CASCADE,
        related_name='adoption_code'
    )
    code = models.CharField(max_length=5, unique=True, default=generate_adoption_code)

    def __str__(self):
        return f"Adoption Code: {self.code} for Landlord ID {self.landlord.id}"

    class Meta:
        db_table = "adoption_codes"



