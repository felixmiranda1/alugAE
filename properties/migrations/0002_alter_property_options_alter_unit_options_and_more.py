# Generated by Django 4.2.17 on 2024-12-27 16:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_adoptioncode_code_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='property',
            options={'verbose_name': 'Property', 'verbose_name_plural': 'Properties'},
        ),
        migrations.AlterModelOptions(
            name='unit',
            options={'verbose_name': 'Unit', 'verbose_name_plural': 'Units'},
        ),
        migrations.RemoveField(
            model_name='property',
            name='address',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='id',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='name',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='property',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='rent_amount',
        ),
        migrations.AddField(
            model_name='property',
            name='city',
            field=models.CharField(default='Unknown', max_length=100, verbose_name='City'),
        ),
        migrations.AddField(
            model_name='property',
            name='complement',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Complement'),
        ),
        migrations.AddField(
            model_name='property',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created At'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='is_standalone',
            field=models.BooleanField(default=False, verbose_name='Standalone Property'),
        ),
        migrations.AddField(
            model_name='property',
            name='landlord',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='properties', to=settings.AUTH_USER_MODEL, verbose_name='Landlord'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='number',
            field=models.CharField(default=1, max_length=10, verbose_name='Number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='state',
            field=models.CharField(default=1, max_length=50, verbose_name='State'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='street',
            field=models.CharField(default=1, max_length=255, verbose_name='Street'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.AddField(
            model_name='property',
            name='zip_code',
            field=models.CharField(default=1, max_length=20, verbose_name='ZIP Code'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='deposit_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Deposit Amount'),
        ),
        migrations.AddField(
            model_name='unit',
            name='monthly_rent',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name='Monthly Rent'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='move_in_date',
            field=models.DateField(blank=True, null=True, verbose_name='Move-in Date'),
        ),
        migrations.AddField(
            model_name='unit',
            name='move_out_date',
            field=models.DateField(blank=True, null=True, verbose_name='Move-out Date'),
        ),
        migrations.AddField(
            model_name='unit',
            name='property_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='properties.property'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('occupied', 'Occupied'), ('maintenance', 'Maintenance'), ('reserved', 'Reserved'), ('inactive', 'Inactive')], default='available', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='unit',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='units', to='accounts.tenant', verbose_name='Tenant'),
        ),
        migrations.AddField(
            model_name='unit',
            name='unit_number',
            field=models.CharField(default=1, max_length=50, verbose_name='Unit Number'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='property',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='property',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Property Name'),
        ),
        migrations.AlterModelTable(
            name='property',
            table='property',
        ),
        migrations.AlterModelTable(
            name='unit',
            table='unit',
        ),
    ]
