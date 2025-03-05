from django import forms

from loans.models import Loan
from payments.models import Payment


class PaymentForm(forms.ModelForm):
    loan_pk = forms.IntegerField()
    loan_pk.widget = loan_pk.hidden_widget()

    class Meta:
        model = Payment
        fields = ['amount', 'due_date', 'payment_method', 'loan', 'loan_pk']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            kwargs.pop('pk')
        super().__init__(*args, **kwargs)

        if pk:
            self.fields['loan'].queryset = Loan.objects.filter(pk=pk)
            self.fields['loan_pk'].initial = pk
        else:
            self.fields['loan'].queryset = Loan.objects.filter(is_paid=False)

    def clean(self):
        super().clean()
        for key in self.errors:
            if "required" in self.fields.get(key).error_messages:
                self.errors[key] = ''
