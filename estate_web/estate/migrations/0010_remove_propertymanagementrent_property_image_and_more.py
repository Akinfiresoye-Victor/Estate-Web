# Generated by Django 5.2.1 on 2025-06-09 14:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0009_alter_propertymanagementrent_property_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propertymanagementrent',
            name='property_image',
        ),
        migrations.RemoveField(
            model_name='propertymanagementsale',
            name='property_image',
        ),
        migrations.AddField(
            model_name='propertymanagementrent',
            name='bathrooms',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='propertymanagementrent',
            name='bedrooms',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='propertymanagementrent',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='RentPropertyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='property_photos/rent/')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='estate.propertymanagementrent')),
            ],
        ),
        migrations.CreateModel(
            name='SalePropertyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='property_photos/sale/')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='estate.propertymanagementsale')),
            ],
        ),
    ]
