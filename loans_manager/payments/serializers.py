from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'due_date', 'payment_method', 'loan']
        extra_kwargs = {'loan': {'read_only': True}}
