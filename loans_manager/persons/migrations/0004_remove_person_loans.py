# Generated by Django 5.1.3 on 2025-01-20 23:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0003_alter_person_bank_account_alter_person_bank_name_and_more'),
        ('loans', '0005_remove_loan_payments_loan_person'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='loans',
        ),
    ]
