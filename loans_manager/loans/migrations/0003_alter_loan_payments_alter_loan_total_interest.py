# Generated by Django 5.1.3 on 2024-12-03 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0002_loan_total_interest_alter_loan_interest_rate_and_more'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='payments',
            field=models.ManyToManyField(blank=True, related_name='loans', to='payments.payment'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='total_interest',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
