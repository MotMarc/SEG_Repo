# Generated by Django 5.1.4 on 2024-12-11 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0015_tutor_hourly_rate_invoice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
    ]