from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from projects.models import ProjectCategory


class SignUpForm(UserCreationForm):
    company = forms.CharField(max_length=30, required=False, help_text='Here you can add your company.')
    phone_number = forms.CharField(max_length=50)

    street_address = forms.CharField(max_length=50)
    city = forms.CharField(max_length=50)
    state = forms.CharField(max_length=50)
    postal_code = forms.CharField(max_length=50)
    country = forms.CharField(max_length=50)

    security_question = forms.CharField(max_length=254)
    security_question_answer = forms.CharField(max_length=254)

    email = forms.EmailField(max_length=254, help_text='Inform a valid email address.')
    categories = forms.ModelMultipleChoiceField(queryset=ProjectCategory.objects.all(),
                                                help_text='Hold down "Control", or "Command" on a Mac, to select more than one.',
                                                required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'categories', 'company', 'email', 'password1', 'password2',
                  'phone_number', 'street_address', 'city', 'state', 'postal_code', 'country')


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.TextInput(attrs={"type": "password"}))


class UserEmailForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean(self):
        cleaned_data = super().clean()

        if User.objects.filter(email=cleaned_data['email']).count() == 0:
            self.add_error('email', 'Email does not correspond to any user.')

        return cleaned_data


class SecurityQuestionForm(forms.Form):
    question = forms.CharField(required=True, disabled=True, initial="Security question")
    answer = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class ConfirmTemporaryPasswordAndCreateNewPasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.password = args[1]
        super(ConfirmTemporaryPasswordAndCreateNewPasswordForm, self).__init__(*args, **kwargs)

    temporaryPassword = forms.CharField(required=True, widget=forms.TextInput(attrs={"type": "password"}),
                                        label="Temporary Password"
                                        )
    newPassword = forms.CharField(required=True, widget=forms.TextInput(attrs={"type": "password"}),
                                  label="New password")

    newPasswordRepeat = forms.CharField(required=True, widget=forms.TextInput(attrs={"type": "password"}),
                                        label="Repeat New password")

    def clean(self):
        cleaned_data = super(ConfirmTemporaryPasswordAndCreateNewPasswordForm, self).clean()

        if len(cleaned_data) == 0:
            return {}

        input_temporary = cleaned_data['temporaryPassword']
        input_password = cleaned_data['newPassword']
        input_password_repeat = cleaned_data['newPasswordRepeat']

        if input_temporary != self.password:
            print("Feil tmp")
            self.add_error('temporaryPassword', 'Temporary password is wrong.')

        if input_password != input_password_repeat:
            print("Feil her også")
            self.add_error('newPassword', 'New and repeated password must be the same.')
            self.add_error('newPasswordRepeat', 'New and repeated password must be the same.')

        return cleaned_data
