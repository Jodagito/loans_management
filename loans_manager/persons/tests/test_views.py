import pytest

from django.urls import reverse

from persons.models import Person
from tests.helpers import TestCase


@pytest.mark.django_db
class TestPersonViewset(TestCase):
    def test_list(self):
        self.create_person()
        url = reverse('person-list')
        response = self.client.get(url)

        self.assert_status_code(response.status_code, 200)
        self.assert_count(len(response.data), 1)

    def test_retrieve(self):
        test_person = self.create_person()
        url = reverse('person-detail', args=(str(test_person.pk)))
        response = self.client.get(url)

        self.assert_status_code(response.status_code, 200)
        self.assert_equal(response.data['person']['id'], test_person.pk)

    def test_create(self):
        test_data = {'name': 'test_user',
                     'phone': '12345',
                     'bank_account': '0000000000',
                     'bank_name': 'test_bank'}

        url = reverse('person-list')
        response = self.client.post(url, data=test_data)
        self.assert_status_code(response.status_code, 201)

        filtered_person = Person.objects.filter(pk=response.data['id'])
        self.assert_bool(filtered_person.exists())

    def test_update(self):
        test_person = self.create_person()
        test_data = {'name': 'updated_name'}

        url = reverse('person-detail', args=(str(test_person.pk)))
        response = self.client.put(url, data=test_data)
        self.assert_status_code(response.status_code, 200)

        filtered_person = Person.objects.filter(pk=response.data['id'])
        self.assert_bool(filtered_person.exists())
        self.assert_equal(filtered_person.first().name, test_data['name'])

    def test_delete(self):
        test_person = self.create_person()

        url = reverse('person-detail', args=(str(test_person.pk)))
        response = self.client.delete(url)
        self.assert_status_code(response.status_code, 204)

        filtered_person = Person.objects.filter(pk=test_person.pk)
        self.assert_bool(filtered_person.exists(), False)
