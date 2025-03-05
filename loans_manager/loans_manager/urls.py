"""
URL configuration for loans_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_nested import routers

from accounts.views import CustomLoginView
from loans.views import (
    LoanViewset,
    LoanViewForm,
)
from payments.views import (
    PaymentViewset,
    PaymentViewForm,
)
from persons.views import (
    PersonViewForm,
    PersonViewset,
)


schema_view = get_schema_view(
   openapi.Info(
      title="Infinity Fire solution APIs",
      default_version='v0.2.0',
      description="Welcome to the API Documentation",
   ),
   public=True,
   permission_classes=[permissions.AllowAny]
)

router = routers.DefaultRouter()
forms_router = routers.DefaultRouter()

router.register(r'persons', PersonViewset)
forms_router.register(r'persons_forms', PersonViewForm, basename='persons-forms')
persons_router = routers.NestedSimpleRouter(router, r'persons', lookup='person')
persons_router.register(r'loans', LoanViewset, basename='person-loans')

router.register(r'loans', LoanViewset)
forms_router.register(r'loans_forms', LoanViewForm, basename='loans-forms')
loans_router = routers.NestedSimpleRouter(persons_router, r'loans', lookup='loan')
loans_router.register(r'payments', PaymentViewset, basename='loan-payments')

router.register(r'payments', PaymentViewset)
forms_router.register(r'payments_forms', PaymentViewForm, basename='payments-forms')

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/', include(persons_router.urls)),
    path('api/', include(loans_router.urls)),
    path('api/', include(router.urls)),
    path('persons_forms/create/', PersonViewForm.as_view(
        {'get': 'create_or_update', 'post': 'create_or_update'}),
         name='persons-forms-create'),
    path('persons_forms/update/<int:pk>', PersonViewForm.as_view(
        {'get': 'create_or_update', 'post': 'create_or_update'}),
         name='persons-forms-update'),
    path('loans_forms/create/', LoanViewForm.as_view(
        {'get': 'create_or_update', 'post': 'create_or_update'}),
         name='loans-forms-create'),
    path('loans_forms/create/<int:pk>', LoanViewForm.as_view(
        {'get': 'create_or_update', 'post': 'create_or_update'}),
         name='loans-forms-create'),
    path('loans_forms/update/<int:pk>', LoanViewForm.as_view(
        {'get': 'create_or_update', 'post': 'create_or_update'}),
         name='loans-forms-update'),
    path('payments_forms/create/', PaymentViewForm.as_view(
        {'get': 'create_or_update', 'post': 'create_or_update'}),
         name='payments-forms-create'),
    path('payments_forms/create/<int:pk>', PaymentViewForm.as_view(
        {'get': 'create_or_update', 'post': 'create_or_update'}),
         name='payments-forms-create'),
    path('payments_forms/update/<int:pk>', PaymentViewForm.as_view(
        {'get': 'create_or_update', 'post': 'create_or_update'}),
         name='payments-forms-update'),
    path('', include(forms_router.urls)),
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
