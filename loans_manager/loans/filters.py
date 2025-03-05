import django_filters
from django import forms

from loans.models import Loan
from persons.models import Person


class LoanFilter(django_filters.FilterSet):
    is_paid = django_filters.BooleanFilter(
        initial=False,
        label='Préstamos pagados',
        widget=forms.Select(choices=[(True, 'Sí'),
                                     (False, 'No'),
                                     (None, 'Todos')]))
    person = django_filters.ModelChoiceFilter(
        label='Deudor',
        queryset=Person.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Loan
        fields = ['is_paid', 'person']


class LoanFilterForPerson(django_filters.FilterSet):
    is_paid = django_filters.BooleanFilter(
        initial=False,
        label='Pago',
        widget=forms.Select(choices=[(True, 'Sí'),
                                     (False, 'No'),
                                     (None, 'Todos')]))

    class Meta:
        model = Loan
        fields = ['is_paid']
