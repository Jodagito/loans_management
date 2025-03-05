from decimal import Decimal
from datetime import date, timedelta

from loans.models import Loan
from payments.models import Payment
from persons.models import Person

from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class TestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username="username")
        self.client.force_login(user)

    def assert_contains(self, first_collection, second_collection):
        for element in first_collection:
            assert element in second_collection, (f"{element} is not in "
                                                  f"{second_collection}")

    def assert_equal(self, value, expected_value):
        assert value == expected_value, (f"{value} is not equal "
                                         f"to {expected_value}")

    def assert_count(self, value, expected_value):
        assert value == expected_value, (f"{value} does not match the expected"
                                         f" count {expected_value}")

    def assert_sum(self, value, expected_value):
        assert value == expected_value, (f"{value} does not match the expected"
                                         f" sum {expected_value}")

    def assert_status_code(self, status, expected_status):
        assert status == expected_status, (f"{status} does not match the "
                                           f"expected status "
                                           f"{expected_status}")

    def assert_bool(self, value, expression=True):
        assert value is expression, f"{value} is not {expression}"

    def create_person(self, name="TestPerson", phone="1234567",
                      bank_account="000000000", bank_name="TestBank"):
        return Person.objects.create(name=name,
                                     phone=phone,
                                     bank_account=bank_account,
                                     bank_name=bank_name)

    def create_loan(self, amount=Decimal('100000'),
                    interest_rate=Decimal('20'),
                    start_date=date.today(), due_date=None,
                    is_paid=False, person=None,
                    total_interest=None):
        if due_date is None:
            due_date = start_date + timedelta(days=30)
        if person is None:
            person = self.create_person()
        if total_interest is None:
            total_interest = amount * interest_rate / 100
        return Loan.objects.create(amount=amount,
                                   interest_rate=interest_rate,
                                   start_date=start_date,
                                   due_date=due_date,
                                   is_paid=is_paid,
                                   person=person,
                                   total_interest=total_interest)

    def create_payment(self, amount=Decimal('100000'), due_date=date.today(),
                       payment_method='Debit', loan=None):
        if loan is None:
            loan = self.create_loan()
        return Payment.objects.create(amount=amount,
                                      due_date=due_date,
                                      payment_method=payment_method,
                                      loan=loan)
