from django import forms

from loans.models import Loan
from persons.models import Person


class LoanForm(forms.ModelForm):
    person_pk = forms.IntegerField()
    person_pk.widget = person_pk.hidden_widget()

    class Meta:
        model = Loan
        fields = ['amount', 'interest_rate', 'start_date',
                  'due_date', 'total_interest', 'person', 'person_pk']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = kwargs.get('instance')
        if pk:
            kwargs.pop('pk')
        super().__init__(*args, **kwargs)

        if pk:
            self.fields['person'].queryset = Person.objects.filter(pk=pk)
            self.fields['person_pk'].initial = pk
        elif instance:
            self.fields['person_pk'].initial = instance.person.pk
        else:
            self.fields['person'].queryset = Person.objects.all()

    def clean(self):
        super().clean()
        for key in self.errors:
            if "required" in self.fields.get(key).error_messages:
                self.errors[key] = ''
