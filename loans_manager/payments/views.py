from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from rest_framework.decorators import action
from rest_framework.viewsets import (
    ModelViewSet,
    ViewSet,
)

from loans.models import Loan
from payments.filters import PaymentFilter
from payments.forms import PaymentForm
from payments.models import Payment
from payments.serializers import PaymentSerializer


class PaymentViewset(LoginRequiredMixin, ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if 'loan_pk' in self.kwargs:
            loan_id = self.kwargs['loan_pk']
            return Loan.objects.get(pk=loan_id).payments
        return self.queryset

    def perform_create(self, serializer):
        loan_pk = self.kwargs['loan_pk']
        loan = Loan.objects.get(pk=loan_pk)
        serializer.validated_data['loan'] = loan
        serializer.save()


class PaymentViewForm(LoginRequiredMixin, ViewSet):
    def list(self, request, pk=None):
        payments = Payment.objects.all()
        payment_filter = PaymentFilter(request.GET, queryset=payments)
        filtered_payments = payment_filter.qs
        return render(request, 'payment_list.html',
                      {'filter': payment_filter,
                       'payments': filtered_payments})

    def create_or_update(self, request, pk=None):
        requested_endpoint = request.build_absolute_uri()
        if pk and 'update' in requested_endpoint:
            payment = get_object_or_404(Payment, pk=pk)
            form = PaymentForm(request.POST or None, instance=payment)
        elif pk and 'create' in requested_endpoint:
            form = PaymentForm(request.POST or None, pk=pk)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                return redirect('loans-forms-update', pk=pk)
        else:
            form = PaymentForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                form.save()

        return render(request, 'payment_form.html', {'form': form})

    @action(detail=True)
    def by_loan(self, request, pk=None):
        payments = Payment.objects.filter(loan=pk)
        return render(request, 'payment_list.html',
                      {'payments': payments})

    @action(detail=True, methods=["get"])
    def delete(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        payment.delete()
        payments = Payment.objects.all()
        return render(request, 'payment_list.html',
                      {'payments': payments})
