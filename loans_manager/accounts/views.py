from django.contrib.auth.views import LoginView
from accounts.forms import LoginForm


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True
