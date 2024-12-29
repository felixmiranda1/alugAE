# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.timezone import now, timedelta

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
def default_expiration():
    """Helper function to define default expiration."""
    return now() + timedelta(days=1)  # Default expiration: 1 day

class AdoptionCode(models.Model):
    landlord = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="adoption_codes",
        verbose_name="Landlord"
    )
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='adoption_codes_property',  # Nome único para evitar conflitos
        null=True,
        blank=True,
        verbose_name="Property"
    )
    unit = models.ForeignKey(
        'properties.Unit',
        on_delete=models.CASCADE,
        related_name='adoption_codes_unit',  # Nome único para evitar conflitos
        null=True,
        blank=True,
        verbose_name="Unit"
    )
    code = models.CharField(max_length=8, unique=True, verbose_name="Adoption Code")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    expires_at = models.DateTimeField(default=default_expiration, verbose_name="Expires At")
    is_used = models.BooleanField(default=False, verbose_name="Is Used")

    def __str__(self):
        return f"Code: {self.code} for Unit: {self.unit} (Property: {self.property})"

    class Meta:
        db_table = "adoption_codes"
        verbose_name = "Adoption Code"
        verbose_name_plural = "Adoption Codes"
