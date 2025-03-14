# Generated by Django 4.2.17 on 2024-12-27 23:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_alter_unit_property_ptr'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unit',
            name='property_ptr',
        ),
        migrations.AddField(
            model_name='unit',
            name='property',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='units', to='properties.property', verbose_name='Property Reference'),
            preserve_default=False,
        ),
    ]
