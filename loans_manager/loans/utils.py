from datetime import date

from loans.models import Loan


def calculate_loans_interest_and_due_date():
    loans = Loan.objects.all()
    for loan in loans:
        if not loan.is_paid and date.today() > loan.due_date:
            loan.calculate_new_due_date()
            loan.calculate_interest()
