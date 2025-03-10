# Generated by Django 5.1.3 on 2025-01-20 23:52

import django.db.models.deletion
from django.db import migrations, models


def find_loan_for_payment(apps, payment):
    Loan = apps.get_model('loans', 'Loan')
    loan = Loan.objects.filter(payments=payment.pk)
    if loan.exists():
        return loan.first()
    return None


def set_loan_field(apps, schema_editor):
    Payment = apps.get_model('payments', 'Payment')
    for payment in Payment.objects.all():
        loan = find_loan_for_payment(apps, payment)
        if loan:
            payment.loan = loan
            payment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0005_remove_loan_payments_loan_person'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='loan',
            field=models.ForeignKey(null=True, blank=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='payments', to='loans.Loan'),
            preserve_default=False,
        ),
        migrations.RunPython(set_loan_field),
        migrations.AlterField(
            model_name='payment',
            name='loan',
            field=models.ForeignKey(
                to='loans.Loan',
                on_delete=models.CASCADE,
                related_name='payments',
            ),
        )
    ]
