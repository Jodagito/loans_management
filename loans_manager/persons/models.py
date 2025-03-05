from django.apps import apps
from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, blank=True)
    bank_account = models.CharField(max_length=255, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)

    def get_loans_sum(self):
        return sum(loan.amount + loan.total_interest
                   for loan in self.loans.all())

    def get_interest_sum(self):
        return sum(loan.total_interest for loan in self.loans.all())

    def get_payments(self):
        Payment = apps.get_model('payments', 'Payment')
        return Payment.objects.filter(loan__in=self.loans.all()).distinct()

    def get_payments_sum(self):
        return sum(payment.amount for payment in self.get_payments())

    def __str__(self):
        return self.name
