"""
WSGI config for loans_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# from loans.utils import calculate_loans_interest_and_due_date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loans_manager.settings')

application = get_wsgi_application()

# calculate_loans_interest_and_due_date()
