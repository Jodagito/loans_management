from rest_framework.serializers import ModelSerializer

from persons.models import Person


class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name', 'phone', 'bank_account', 'bank_name', 'loans']
        read_only_fields = ['loans']
