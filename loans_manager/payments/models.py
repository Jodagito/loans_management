from django.db import models

from loans.models import Loan


class PaymentMethod(models.TextChoices):
    DEBIT = 'debit', 'Debit'
    CASH = 'cash', 'Cash'


class Payment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    due_date = models.DateField()
    payment_method = models.CharField(choices=PaymentMethod.choices,
                                      max_length=5)
    loan = models.ForeignKey(Loan, related_name="payments",
                             on_delete=models.CASCADE)

    def __str__(self):
        return f'Payment by {self.loan.person} for Loan {self.loan.id}'
