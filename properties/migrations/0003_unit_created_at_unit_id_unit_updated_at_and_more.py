# Generated by Django 4.2.17 on 2024-12-27 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0002_alter_property_options_alter_unit_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=1, verbose_name='Created At'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.AlterField(
            model_name='unit',
            name='property_ptr',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, related_name='unit', to='properties.property', verbose_name='Property Reference'),
        ),
    ]
