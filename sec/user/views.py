from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sessions.backends.cache import SessionStore
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView
from django.contrib.auth import authenticate
import re
from .forms import SignUpForm, LoginForm

from ratelimit.mixins import RatelimitMixin


class IndexView(TemplateView):
    template_name = "sec/base.html"


def logout(request):
    request.session = SessionStore()
    return HttpResponseRedirect(reverse_lazy("home"))


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

        password = form.cleaned_data["password1"]

        if len(password) < 8:
            form.add_error(None, "Password should be longer than 8")
            return super().form_invalid(form)
        if not re.match("(.*[a-z].*)", password):
            form.add_error(None, "You need at least one lowercase letter")
            return super().form_invalid(form)
        if not re.match("(.*[A-Z].*)", password):
            form.add_error(None, "You neet at least one uppercase letter in the password")
            return super().form_invalid(form)
        if not re.match("(.*[!\"#$%&/()=?].*)", password):
            form.add_error(None, "You need to at least one special character !\"#$%&/()=? in the password")
            return super().form_invalid(form)

        user.save()

        login(self.request, user)

        return HttpResponseRedirect(self.success_url)
