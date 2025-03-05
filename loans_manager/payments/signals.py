from django.db.models.signals import post_save
from django.dispatch import receiver

from payments.models import Payment


@receiver(post_save, sender=Payment)
def update_loan_on_payment(sender, instance, created, **kwargs):
    loan = instance.loan
    if loan:
        loan.update_amount()
