import os

from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView, RedirectView
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string

from user.RandomPasswordGenerator import RandomPasswordGenerator
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from user.models import Profile
from .forms import SignUpForm, LoginForm, SecurityQuestionForm, UserEmailForm, \
    ConfirmTemporaryPasswordAndCreateNewPasswordForm
from django.shortcuts import render
from django.urls import reverse

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
        user.profile.security_question = form.cleaned_data["security_question"]
        user.profile.security_question_answer = form.cleaned_data["security_question_answer"]

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


class UserEmailView(TemplateView):
    form_class = UserEmailForm
    template_name = "user/user_email.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form['email'].value()
            url = reverse('sec_question', kwargs={'email': email})
            return HttpResponseRedirect(url)

        return render(request, self.template_name, {'form': form})


class SecurityQuestionView(TemplateView, FormView):
    form_class = SecurityQuestionForm
    template_name = "user/sec_question.html"
    answer = ""

    def get(self, request, *args, **kwargs):
        user = User.objects.get(email=kwargs['email'])
        profile = Profile.objects.get(user=user)
        self.answer = profile.security_question_answer
        initial = {'question': profile.security_question}
        form = self.form_class(initial=initial)
        return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
        # Get the email by parsing the path
        path = self.request.META['PATH_INFO']
        email = os.path.basename(os.path.normpath(path))

        user = User.objects.get(email=email)
        correct_answer = user.profile.security_question_answer
        entered_answer = form.cleaned_data['answer']

        if form.is_valid():
            if correct_answer == entered_answer:
                # Make sure we adhere to the password rules defined in 'settings.py'.
                random_password = RandomPasswordGenerator.generate(9)

                # Send forgot password email
                message = render_to_string('user/forgot_password_email.html', {
                    'user': user,
                    'random_password': random_password
                })

                _email = EmailMessage(
                    "Confirm email", message, to=[email]
                )
                _email.send()
                self.request.session['email'] = email
                self.request.session['password'] = random_password
                return HttpResponseRedirect(reverse('conf_new_password'))
            else:
                initial = {'question': user.profile.security_question}
                form = self.form_class(initial=initial)
                return render(self.request, self.template_name, {'form': form})


class ConfirmTemporaryPasswordAndCreateNewPassword(TemplateView, FormView):
    form_class = ConfirmTemporaryPasswordAndCreateNewPasswordForm
    template_name = "../../user/templates/user/confirm_temporary_password_and_create_new_password.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.POST, self.request.session['password'])
        return render(self.request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, self.request.session['password'])

        if form.is_valid():
            cleaned_data = form.cleaned_data
            email = request.session['email']
            user = User.objects.get(email=email)
            user.set_password(cleaned_data['newPassword'])
            user.save()
            return HttpResponseRedirect(reverse('login'))
        else:
            return render(self.request, self.template_name, {'form': form})
