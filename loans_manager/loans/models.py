from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.db import models

from persons.models import Person


class Loan(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    original_amount = models.DecimalField(max_digits=10, decimal_places=0,
                                          editable=False, default=Decimal('0'))
    interest_rate = models.DecimalField(max_digits=5, decimal_places=1)
    start_date = models.DateField()
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    person = models.ForeignKey(Person, related_name="loans",
                               on_delete=models.CASCADE)
    total_interest = models.DecimalField(max_digits=10, decimal_places=0,
                                         default=Decimal(0.0), blank=True)

    def __str__(self):
        return f'Loan {self.id} for {self.person}'

    def calculate_interest(self):
        self.total_interest += self.amount * self.interest_rate / 100

    def calculate_new_due_date(self):
        months = (date.today() - self.start_date).days // 30
        self.due_date += relativedelta(months=months)

    def update_amount(self):
        last_payment = self.payments.last().amount
        remaining_interest = max(self.total_interest - last_payment, 0)
        if remaining_interest == 0:
            last_payment -= self.total_interest
            self.total_interest = Decimal('0')
            self.amount = max(self.amount - last_payment, 0)
        self.is_paid = self.amount == 0
        if not self.is_paid and self.payments.last().due_date > self.due_date:
            self.calculate_new_due_date()
            self.calculate_interest()
        self.save()

    def get_paid_amount(self):
        return sum(payment.amount for payment in self.payments.all())

    def get_remaining_debt(self):
        return self.amount + self.total_interest

    def get_current_earnings_amount(self):
        total_paid = self.get_paid_amount()
        return abs(total_paid - (self.original_amount - self.amount))

    def get_summary(self):
        dict = {
            'original_amount': self.original_amount,
            'amount': self.amount,
            'interest_rate': self.interest_rate,
            'total_interest': self.total_interest,
        }
        return dict

    def save(self, *args, **kwargs):
        if not self.pk:
            self.original_amount = self.amount
            self.calculate_interest()
        super().save(*args, **kwargs)
