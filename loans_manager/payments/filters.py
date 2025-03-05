import django_filters
from django import forms

from payments.models import Payment
from persons.models import Person


class PaymentFilter(django_filters.FilterSet):
    person = django_filters.ModelChoiceFilter(
        label='Deudor',
        queryset=Person.objects.all(),
        method='filter_payments_by_person',
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Payment
        fields = ['person']

    def filter_payments_by_person(self, queryset, name, value):
        if value:
            return queryset.filter(loan__person=value).distinct()
        return queryset
