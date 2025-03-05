import pytest

from payments.models import Payment
from persons.models import Person
from tests.helpers import TestCase


@pytest.mark.django_db
class TestPersonModels(TestCase):
    def test_create_person(self):
        Person.objects.create(name="TestName",
                              phone="123456",
                              bank_account="0000000000",
                              bank_name="TestBank")
        self.assert_count(Person.objects.count(), 1)

    def test_update_person(self):
        test_person = self.create_person()
        new_name = "UpdatedName"
        test_person.name = new_name
        test_person.save()

        self.assert_equal(Person.objects.first().name, new_name)

    def test_delete_person(self):
        test_person = self.create_person()
        self.assert_count(Person.objects.count(), 1)
        test_person.delete()
        self.assert_count(Person.objects.count(), 0)

    def test_get_loans_sum(self):
        test_person = self.create_person()
        loan = self.create_loan(person=test_person)
        expected_sum = loan.amount + loan.total_interest

        self.assert_sum(test_person.get_loans_sum(), expected_sum)

    def test_get_interest_sum(self):
        test_person = self.create_person()
        loan_0 = self.create_loan(person=test_person)
        loan_1 = self.create_loan(person=test_person)
        loan_2 = self.create_loan(person=test_person)
        expected_sum = (loan_0.total_interest +
                        loan_1.total_interest +
                        loan_2.total_interest)

        self.assert_sum(test_person.get_interest_sum(), expected_sum)

    def test_get_payments(self):
        test_person = self.create_person()
        loan = self.create_loan(person=test_person)
        self.create_payment(loan=loan)
        self.create_payment(loan=loan)

        all_payments = Payment.objects.filter(loan=loan)

        self.assert_contains(all_payments, test_person.get_payments())

    def test_get_payments_sum(self):
        test_person = self.create_person()
        loan = self.create_loan(person=test_person)
        self.create_payment(loan=loan)
        self.create_payment(loan=loan)

        all_payments = Payment.objects.filter(loan=loan)
        expected_sum = sum([payment.amount for payment in all_payments])

        self.assert_sum(test_person.get_payments_sum(), expected_sum)
