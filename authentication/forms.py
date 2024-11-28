from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password

from .models import Account


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(), label="Password", validators=[validate_password]
    )
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")
    # checker_image = forms.ImageField(label="Checker Image", required=False)

    class Meta:
        model = Account
        fields = ["username", "password1", "password2"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    image = forms.ImageField(required=False)

    class Meta:
        model = Account
        fields = ["username", "password", "image"]
