from django.contrib import admin

from loans.models import Loan
from payments.models import Payment
from persons.models import Person


admin.site.register(Loan)
admin.site.register(Payment)
admin.site.register(Person)
