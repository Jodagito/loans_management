from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import (
    ModelViewSet,
    ViewSet,
)

from loans_manager.utils import build_report
from persons.filters import PersonFilter
from persons.models import Person
from persons.forms import PersonForm
from persons.serializers import PersonSerializer
from payments.serializers import PaymentSerializer
from loans.serializers import LoanSerializer


class PersonViewset(LoginRequiredMixin, ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def get_serializer_class(self):
        if self.action == "create_loan":
            return LoanSerializer
        elif self.action == "add_payment":
            return PaymentSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        person = self.get_object()
        data = {
            "person": PersonSerializer(person).data,
            "loans": LoanSerializer(person.loans.all(), many=True).data,
            "payments": PaymentSerializer(person.get_payments(),
                                          many=True).data,
            "total_debt_amount": person.get_loans_sum(),
            "total_interest_amount": person.get_interest_sum(),
            "total_payments_amount": person.get_payments_sum(),
        }
        return Response(data)

    def list(self, request, *args, **kwargs):
        persons = self.get_queryset().order_by('name')
        data = [
            {
                "person": PersonSerializer(person).data,
            }
            for person in persons
        ]
        return Response(data)

    @action(detail=True, methods=["get"], url_path="generate-loans-report")
    def generate_loans_report(self, request, pk=None):
        person = self.get_object()
        loans = person.loans.filter(is_paid=False)
        if not loans.exists():
            return Response({"detail": "No loans found for this person."},
                            status=status.HTTP_404_NOT_FOUND)
        loan_data = {
            "Inicio": [loan.start_date.strftime("%d-%m-%Y") for loan in loans],
            "Fin": [loan.due_date.strftime("%d-%m-%Y") for loan in loans],
            "Valor": [f"{loan.amount:,.0f}" for loan in loans],
            "Tasa": [f"{loan.interest_rate:.0f}%" for loan in loans],
            "Interés": [f"{loan.total_interest:,.0f}" for loan in loans],
            "Pagado": [f"{loan.get_paid_amount():,.0f}" for loan in loans],
            "Restante": [
                f"{loan.get_remaining_debt():,.0f}" for loan in loans
            ],
        }
        total_original = sum(loan.original_amount for loan in loans)
        total_paid = sum(Decimal(amount.replace(",", ""))
                         for amount in loan_data["Pagado"])
        total_remaining = sum(Decimal(amount.replace(",", ""))
                              for amount in loan_data["Restante"])
        summary_text = f"""
        <b>Fecha:</b> {date.today()}<br/>
        <b>Capital Total Original:</b> ${total_original:,.0f}<br/>
        <b>Total Pagado:</b> ${total_paid:,.0f}<br/>
        <b>Total Restante:</b> ${total_remaining:,.0f}
        """
        if loans.count() > 1:
            summary_text = f"<b>Cantidad de Préstamos:</b> {loans.count()}<br/>" + summary_text
        columns = [["Inicio", "Fin", "Valor", "Tasa",
                    "Interés", "Pagado", "Restante"]]
        filename = f"Reporte de Préstamos para {person.name}"
        return build_report(loan_data, filename, summary_text, columns)

    @action(detail=True, methods=["get"], url_path="generate-payments-report")
    def generate_payments_report(self, request, pk=None):
        person = self.get_object()
        payments = person.get_payments()

        if not payments.exists():
            return Response({"detail": "No payments found for this person."},
                            status=status.HTTP_404_NOT_FOUND)

        payment_method_mapping = {'debit': 'Débito', 'cash': 'Efectivo'}
        payment_data = {
            "Fecha": [payment.due_date.strftime("%d-%m-%Y")
                      for payment in payments],
            "Valor": [f"{payment.amount:,.0f}" for payment in payments],
            "Método": [payment_method_mapping.get(payment.payment_method)
                       for payment in payments],
        }
        total_paid = sum(Decimal(amount.replace(",", ""))
                         for amount in payment_data["Valor"])
        filename = f"Reporte de Pagos para {person.name}"
        summary_text = f"""
        <b>Total Pagado:</b> ${total_paid:,.0f}<br/>
        """
        if payments.count() > 1:
            summary_text = f"<b>Cantidad de Pagos:</b> {payments.count()}<br/>" + summary_text
        columns = [["Fecha", "Valor", "Método"]]
        return build_report(payment_data, filename, summary_text, columns)


class PersonViewForm(LoginRequiredMixin, ViewSet):
    def list(self, request, pk=None):
        persons = Person.objects.all()
        person_filter = PersonFilter(request.GET, queryset=persons)
        filtered_persons = person_filter.qs
        return render(request, 'person_list.html',
                      {'filter': person_filter, 'persons': filtered_persons})

    def create_or_update(self, request, pk=None):
        if pk:
            person = get_object_or_404(Person, pk=pk)
            form = PersonForm(request.POST or None, instance=person)
            if form.is_valid():
                form.save()
            return render(request, 'person_form.html', {'form': form})
        else:
            form = PersonForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('persons-forms-list')

        return render(request, 'person_form.html', {'form': form})

    @action(detail=True, methods=["get"])
    def delete(self, request, pk):
        person = get_object_or_404(Person, pk=pk)
        person.delete()
        persons = Person.objects.all()
        return render(request, 'person_list.html',
                      {'persons': persons})
