from rest_framework.serializers import ModelSerializer

from loans.models import Loan


class LoanSerializer(ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'amount', 'interest_rate', 'start_date',
                  'due_date', 'is_paid', 'payments', 'total_interest', 'person']
        read_only_fields = ['is_paid', 'payments', 'total_interest', 'person']


class LoanUpdateSerializer(ModelSerializer):
    class Meta:
        model = Loan
        fields = ['amount', 'interest_rate', 'total_interest',
                  'start_date', 'due_date']
        extra_kwargs = {}
        for field in fields:
            extra_kwargs[field] = {'required': False}
