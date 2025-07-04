# Generated by Django 5.2.1 on 2025-06-02 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0002_alter_propertymanagementsale_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyManagementRent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Description')),
                ('location', models.CharField(max_length=255, verbose_name='Location')),
                ('phone_number', models.IntegerField(verbose_name='Phone Number')),
                ('price_range', models.CharField(verbose_name='Price Range')),
                ('available', models.BooleanField(default=True, verbose_name='Availble')),
            ],
        ),
    ]
