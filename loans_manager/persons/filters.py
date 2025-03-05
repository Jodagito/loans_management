import django_filters
from django import forms

from persons.models import Person


class PersonFilter(django_filters.FilterSet):
    has_active_loans = django_filters.BooleanFilter(
        label='Personas con préstamos activos',
        method='filter_has_active_loans',
        widget=forms.Select(attrs={'class': 'form-control'},
                            choices=[(True, 'Sí'),
                                     (False, 'No')]))

    class Meta:
        model = Person
        fields = ['has_active_loans']

    def filter_has_active_loans(self, queryset, name, value):
        if value:
            return queryset.filter(loans__is_paid=False).distinct()
        return queryset
