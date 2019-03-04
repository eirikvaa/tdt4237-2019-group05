from django.contrib.auth import login, logout
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sessions.backends.cache import SessionStore
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView, RedirectView
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from .forms import SignUpForm, LoginForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from ratelimit.mixins import RatelimitMixin


class IndexView(TemplateView):
    template_name = "sec/base.html"


class LogoutView(RedirectView):
    pattern_name = "login"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class LoginView(RatelimitMixin, FormView):
    ratelimit_key = 'ip'
    ratelimit_method = 'POST'
    ratelimit_rate = '3/m'
    ratelimit_block = True

    form_class = LoginForm
    template_name = "user/login.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        password = form.cleaned_data["password"]
        username = form.cleaned_data["username"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, "Provide a valid username and/or password")
            return super().form_invalid(form)


class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "user/signup.html"
    success_url = reverse_lazy("home")


    def form_valid(self, form):
        user = form.save()

        categories = form.cleaned_data["categories"]
        user.profile.company = form.cleaned_data["company"]
        user.profile.categories.add(*categories)

        user.is_active = False

        user.save()

        message = render_to_string('user/acc_active_email.html', {
            'user': user,
            'domain': "127.0.0.1:8000",
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': account_activation_token.make_token(user),
        })

        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
            "Confirm email", message, to=[to_email]
        )
        email.send()
        return HttpResponse('Please confirm your email address to complete the registration')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')