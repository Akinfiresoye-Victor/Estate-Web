# Generated by Django 5.2.1 on 2025-06-26 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0016_alter_propertymanagementrent_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertymanagementsale',
            name='price',
            field=models.CharField(default=1, verbose_name='Price'),
        ),
    ]
