from django.db import models
from django.conf import settings
from properties.models import Unit
from accounts.models import Landlord, Tenant

class Template(models.Model):
    name = models.CharField(max_length=100)  # Template name
    content = models.TextField()  # Template content with placeholders
    is_default = models.BooleanField(default=False)  # Indicates if the template is a default one
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # The user who created the template
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of template creation

    def __str__(self):
        return self.name


class Contract(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    landlord = models.ForeignKey(
        Landlord,
        related_name="contracts_as_landlord",
        on_delete=models.CASCADE
    )  # The landlord associated with the contract
    tenant = models.ForeignKey(
        Tenant,
        related_name="contracts_as_tenant",
        on_delete=models.CASCADE
    )  # The tenant associated with the contract
    template = models.ForeignKey(
        Template,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # Template used for the contract
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    start_date = models.DateField()  # Start date of the contract
    end_date = models.DateField()  # End date of the contract
    rent_value = models.DecimalField(max_digits=10, decimal_places=2)  # Monthly rent value
    payment_due_date = models.PositiveIntegerField()  # Payment due date
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )  # Current status of the contract
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of contract creation

    def __str__(self):
        return f"Contract between {self.landlord} and {self.tenant}"


class Clause(models.Model):
    contract = models.ForeignKey(
        Contract,
        related_name="clauses",
        on_delete=models.CASCADE
    )  # The contract this clause is associated with
    content = models.TextField()  # Content of the customized clause
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # The user who added the clause

    def __str__(self):
        return f"Clause for Contract ID {self.contract.id}"


class Document(models.Model):
    contract = models.ForeignKey(
        Contract,
        related_name="documents",
        on_delete=models.CASCADE
    )  # The contract associated with this document
    file = models.FileField(upload_to='contracts/documents/')  # File path for the document
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of document creation

    def __str__(self):
        return f"Document for Contract ID {self.contract.id}"
