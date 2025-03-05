from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    render,
    get_object_or_404,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import (
    ModelViewSet,
    ViewSet,
)

from loans_manager.utils import (
    build_report,
    build_excel_report,
)
from loans.filters import (
    LoanFilter,
    LoanFilterForPerson,
)
from loans.forms import LoanForm
from loans.models import Loan
from loans.serializers import (
    LoanSerializer,
    LoanUpdateSerializer,
)
from persons.models import Person
from persons.serializers import PersonSerializer
from payments.models import Payment
from payments.serializers import PaymentSerializer


class LoanViewset(LoginRequiredMixin, ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def perform_create(self, serializer):
        person_id = self.kwargs['person_pk']
        person = Person.objects.get(pk=person_id)
        serializer.validated_data['person'] = person
        serializer.save()

    def update(self, request, *args, **kwargs):
        self.serializer_class = LoanUpdateSerializer
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if 'person_pk' in kwargs:
            return self.retrieve_person_loan(kwargs.get('person_pk'),
                                             kwargs.get('pk'))
        self.serializer_class = LoanUpdateSerializer
        loan = self.get_object()
        payments = Payment.objects.filter(loan=loan)
        total_paid = sum(payment.amount for payment in loan.payments.all())
        data = {
            "person": PersonSerializer(Person.objects.get(loans=loan)).data,
            "loan": LoanSerializer(loan).data,
            "payments": PaymentSerializer(payments, many=True).data,
            "total_paid": total_paid,
            "total_missing": (loan.amount + loan.total_interest) - total_paid,
        }
        return Response(data)

    def retrieve_person_loan(self, person_pk, loan_pk):
        self.serializer_class = LoanUpdateSerializer
        person = Person.objects.get(pk=person_pk)
        loan = person.loans.get(pk=loan_pk)
        payments = loan.payments.all()
        data = {
            "person": PersonSerializer(person).data,
            "loan": LoanSerializer(loan).data,
            "payments": PaymentSerializer(payments, many=True).data,
            "total_paid": loan.get_paid_amount(),
            "total_missing": loan.get_remaining_debt(),
        }
        return Response(data)

    def list(self, request, *args, **kwargs):
        if 'person_pk' in kwargs:
            return self.list_person_loans(kwargs.get('person_pk'))
        loans = self.get_queryset()
        data = [
            {
                "person": PersonSerializer(Person.objects.get(loans=loan)).data,
                "loan": LoanSerializer(loan).data,
                "payments": PaymentSerializer(
                    loan.payments.all(), many=True).data,
            }
            for loan in loans
        ]
        return Response(data)

    def list_person_loans(self, person_pk):
        person = Person.objects.get(pk=person_pk)
        loans = person.loans.all()
        data = {"person": PersonSerializer(person).data,
                "loans": [{"loan": LoanSerializer(loan).data} for loan in loans]}
        return Response(data)

    @action(detail=True, methods=["get"], url_path="generate-loan-report")
    def generate_loan_report(self, request, pk=None, person_pk=None):
        loan = self.get_object()
        person = Person.objects.filter(loans=loan).first()

        loan_data = {
            "Inicio": [loan.start_date.strftime("%d-%m-%Y")],
            "Fin": [loan.due_date.strftime("%d-%m-%Y")],
            "Valor": [f"{loan.amount:,.0f}"],
            "Tasa": [f"{loan.interest_rate:.0f}%"],
            "Interés": [f"{loan.total_interest:,.0f}"],
            "Pagado": [f"{loan.get_paid_amount():,.0f}"],
            "Restante": [f"{loan.get_remaining_debt():,.0f}"],
        }

        total_original = loan.original_amount
        total_paid = sum(Decimal(amount.replace(",", "")) for amount in loan_data["Pagado"])
        total_remaining = sum(Decimal(amount.replace(",", "")) for amount in loan_data["Restante"])

        filename = f"Reporte de Préstamo para {person.name}"

        summary_text = f"""
        <b>Fecha Generación:</b> {date.today()}<br/>
        <b>Capital Total Original:</b> ${total_original:,.0f}<br/>
        <b>Total Pagado:</b> ${total_paid:,.0f}<br/>
        <b>Total Restante:</b> ${total_remaining:,.0f}
        """

        columns = [["Inicio", "Fin", "Valor", "Tasa",
                    "Interés", "Pagado", "Restante"]]

        return build_report(loan_data, filename, summary_text, columns)

    @action(detail=False, methods=["get"], url_path="generate-complete-report")
    def generate_complete_report(self, request, pk=None, by_state=None):
        filename = "Reporte Completo de Préstamos"
        loans = self.queryset.filter().order_by('start_date')
        if by_state == 'Unpaid':
            filename = "Reporte Completo de Préstamos No Pagos"
            loans = self.queryset.filter(is_paid=False).order_by('start_date')
        elif by_state == 'Paid':
            filename = "Reporte Completo de Préstamos Pagos"
            loans = self.queryset.filter(is_paid=True).order_by('start_date')

        if not loans.exists():
            return Response({"detail": "No loans found for this person."},
                            status=status.HTTP_404_NOT_FOUND)

        loans_data = {
            "Deudor": [Person.objects.filter(loans=loan).first().name for loan in loans],
            "Inicio": [loan.start_date.strftime("%d-%m-%Y") for loan in loans],
            "Fin": [loan.due_date.strftime("%d-%m-%Y") for loan in loans],
            "Valor": [f"{loan.amount:,.0f}" for loan in loans],
            "Interés": [f"{loan.total_interest:,.0f}" for loan in loans],
            "Pagado": [f"{loan.get_paid_amount():,.0f}" for loan in loans],
            "Restante": [
                f"{loan.get_remaining_debt():,.0f}" for loan in loans
            ],
        }
        original_amount = [f"{loan.original_amount:,.0f}" for loan in loans]
        earnings_amount = [f"{loan.get_current_earnings_amount():,.0f}" for loan in loans]

        total_original = sum(Decimal(amount.replace(",", "")) for amount in original_amount)
        total_earnings = sum(Decimal(amount.replace(",", "")) for amount in earnings_amount)
        total_paid = sum(Decimal(amount.replace(",", "")) for amount in loans_data["Pagado"])
        total_remaining = sum(Decimal(amount.replace(",", "")) for amount in loans_data["Restante"])
        total_remaining_interests = sum(Decimal(amount.replace(",", "")) for amount in loans_data["Interés"])
        total_profitability = (total_earnings / total_original) * 100
        total_paid_debt = abs(total_earnings - total_paid)
        projected_earnings = total_remaining_interests + total_earnings
        projected_profit = (projected_earnings / total_original) * 100
        total_original_remaining = total_remaining - total_remaining_interests

        summary_text = f"""
        <b>Fecha Generación:</b> {date.today()}<br/>
        <b>Capital Total Original:</b> ${total_original:,.0f}<br/>
        <b>Total Rentabilidad Actual:</b> {total_profitability:,.2f}%<br/>
        <b>Total Rentabilidad Proyectada:</b> {projected_profit:,.2f}%<br/>
        <b>Total Interés Restante:</b> ${total_remaining_interests:,.0f}<br/>
        <b>Total Intereses Pagados:</b> ${total_earnings:,.0f}<br/>
        <b>Total Capital Pagado:</b> ${total_paid_debt:,.0f}<br/>
        <b>Total Pagado:</b> ${total_paid:,.0f}<br/>
        <b>Total Ganancias Proyectadas:</b> ${projected_earnings:,.0f}<br/>
        <b>Total Capital Restante:</b> ${total_original_remaining:,.0f}<br/>
        <b>Total Restante:</b> ${total_remaining:,.0f}
        """
        if loans.count() > 1:
            summary_text = f"<b>Cantidad de Préstamos:</b> {loans.count()}<br/>" + summary_text

        columns = [["Deudor", "Inicio", "Fin", "Valor", "Interés", "Pagado", "Restante"]]

        return build_report(loans_data, filename, summary_text, columns)

    @action(detail=False, methods=["get"], url_path="generate-unpaid-loans-report")
    def generate_unpaid_loans_report(self, request, pk=None):
        return self.generate_complete_report(request, pk, by_state='Unpaid')

    @action(detail=False, methods=["get"], url_path="generate-paid-loans-report")
    def generate_paid_loans_report(self, request, pk=None):
        return self.generate_complete_report(request, pk, by_state='Paid')

    @action(detail=False, methods=["get"], url_path="generate-complete-excel-report")
    def generate_complete_excel_report(self, requests, pk=None):
        filename = "Reporte Completo de Préstamos"
        loans = self.queryset.filter().order_by('start_date')

        if not loans.exists():
            return Response({"detail": "No loans found for this person."},
                            status=status.HTTP_404_NOT_FOUND)

        loans_data = {
            "Deudor": [Person.objects.filter(loans=loan).first().name for loan in loans],
            "Inicio": [loan.start_date.strftime("%d-%m-%Y") for loan in loans],
            "Fin": [loan.due_date.strftime("%d-%m-%Y") for loan in loans],
            "Valor": [f"{loan.amount:,.0f}" for loan in loans],
            "Interés": [f"{loan.total_interest:,.0f}" for loan in loans],
            "Pagado": [f"{loan.get_paid_amount():,.0f}" for loan in loans],
            "Restante": [
                f"{loan.get_remaining_debt():,.0f}" for loan in loans
            ],
        }
        original_amount = [f"{loan.original_amount:,.0f}" for loan in loans]
        earnings_amount = [f"{loan.get_current_earnings_amount():,.0f}" for loan in loans]

        total_original = sum(Decimal(amount.replace(",", "")) for amount in original_amount)
        total_earnings = sum(Decimal(amount.replace(",", "")) for amount in earnings_amount)
        total_paid = sum(Decimal(amount.replace(",", "")) for amount in loans_data["Pagado"])
        total_remaining = sum(Decimal(amount.replace(",", "")) for amount in loans_data["Restante"])
        total_remaining_interests = sum(Decimal(amount.replace(",", "")) for amount in loans_data["Interés"])
        total_profitability = (total_earnings / total_original) * 100
        total_paid_debt = abs(total_earnings - total_paid)
        projected_earnings = total_remaining_interests + total_earnings
        projected_profit = (projected_earnings / total_original) * 100
        total_original_remaining = total_remaining - total_remaining_interests

        summary_text = f"""
        Cantidad de Préstamos: {loans.count()}
        Fecha Generación: {date.today()}
        Capital Total Original: ${total_original:,.0f}
        Total Rentabilidad Actual: {total_profitability:,.2f}%
        Total Rentabilidad Proyectada: {projected_profit:,.2f}%
        Total Interés Restante: ${total_remaining_interests:,.0f}
        Total Intereses Pagados: ${total_earnings:,.0f}
        Total Capital Pagado: ${total_paid_debt:,.0f}
        Total Pagado: ${total_paid:,.0f}
        Total Ganancias Proyectadas: ${projected_earnings:,.0f}
        Total Capital Restante: ${total_original_remaining:,.0f}
        Total Restante: ${total_remaining:,.0f}
        """

        columns = ["Deudor", "Inicio", "Fin", "Valor",
                   "Interés", "Pagado", "Restante"]

        return build_excel_report(loans_data, filename, summary_text, columns)


class LoanViewForm(LoginRequiredMixin, ViewSet):
    def list(self, request, pk=None):
        loans = Loan.objects.all()
        loan_filter = LoanFilter(request.GET, queryset=loans)
        filtered_loans = loan_filter.qs
        return render(request, 'loan_list.html',
                      {'filter': loan_filter, 'loans': filtered_loans})

    def create_or_update(self, request, pk=None):
        requested_endpoint = request.build_absolute_uri()
        if pk and 'update' in requested_endpoint:
            loan = get_object_or_404(Loan, pk=pk)
            form = LoanForm(request.POST or None, instance=loan)
        elif pk and 'create' in requested_endpoint:
            form = LoanForm(request.POST or None, pk=pk)
        else:
            form = LoanForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                form.save()

        return render(request, 'loan_form.html', {'form': form})

    @action(detail=True)
    def by_person(self, request, pk=None):
        loans = Loan.objects.filter(person=pk)
        loan_filter = LoanFilterForPerson(request.GET, queryset=loans)
        filtered_loans = loan_filter.qs
        return render(request, 'loan_list.html',
                      {'filter': loan_filter, 'loans': filtered_loans})

    @action(detail=True, methods=["get"])
    def delete(self, request, pk):
        loan = get_object_or_404(Loan, pk=pk)
        loan.delete()
        loans = Loan.objects.all()
        return render(request, 'loan_list.html',
                      {'loans': loans})
