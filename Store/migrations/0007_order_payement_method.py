# Generated by Django 5.1.7 on 2025-04-18 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0006_category_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payement_method',
            field=models.CharField(choices=[('cash', 'Cash'), ('cib', 'CIB'), ('edahabia', 'Edahabia')], default='cash', max_length=10),
        ),
    ]
