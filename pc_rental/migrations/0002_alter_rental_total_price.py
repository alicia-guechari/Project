# Generated by Django 5.1.7 on 2025-04-14 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pc_rental', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rental',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=8),
        ),
    ]
