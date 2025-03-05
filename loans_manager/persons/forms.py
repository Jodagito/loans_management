from django import forms

from persons.models import Person


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'phone', 'bank_account', 'bank_name']

    def clean(self):
        super().clean()
        for key in self.errors:
            if "required" in self.fields.get(key).error_messages:
                self.errors[key] = ''
