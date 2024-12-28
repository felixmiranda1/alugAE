from django.db import models
from django.conf import settings


class Property(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Property Name")
    street = models.CharField(max_length=255, verbose_name="Street")
    number = models.CharField(max_length=10, verbose_name="Number")
    complement = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complement")
    city = models.CharField(max_length=100, default="Unknown", verbose_name="City")
    state = models.CharField(max_length=50, verbose_name="State")
    zip_code = models.CharField(max_length=20, verbose_name="ZIP Code")
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
        verbose_name="Landlord"
    )
    is_standalone = models.BooleanField(default=False, verbose_name="Standalone Property")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.name} - {self.street}, {self.city}"

    class Meta:
        db_table = 'property'
        verbose_name = "Property"
        verbose_name_plural = "Properties"


class Unit(models.Model):
    id = models.BigAutoField(primary_key=True) 
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="units",
        verbose_name="Property Reference"
    )

    unit_number = models.CharField(max_length=50, verbose_name="Unit Number")
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('occupied', 'Occupied'),
            ('maintenance', 'Maintenance'),
            ('reserved', 'Reserved'),
            ('inactive', 'Inactive')
        ],
        default='available',
        verbose_name="Status"
    )
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='units',
        verbose_name="Tenant"
    )
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monthly Rent")
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Deposit Amount"
    )
    move_in_date = models.DateField(blank=True, null=True, verbose_name="Move-in Date")
    move_out_date = models.DateField(blank=True, null=True, verbose_name="Move-out Date")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Unit {self.unit_number} - {self.property_ptr.name}"

    class Meta:
        db_table = 'unit'
        verbose_name = "Unit"
        verbose_name_plural = "Units"
