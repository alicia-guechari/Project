# Generated by Django 5.1.7 on 2025-04-29 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pc_rental', '0008_pc_aviability_date_alter_rental_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rental',
            name='status',
        ),
        migrations.AlterField(
            model_name='rental',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
