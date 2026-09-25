from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)

from .models import User

INPUT_CLASSES = (
    'w-full rounded-lg border border-gray-300 px-4 py-2 '
    'focus:border-black focus:outline-none focus:ring-2 focus:ring-black/20'
)


class StyledFormMixin:
    """Applique les classes Tailwind à tous les champs du formulaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', INPUT_CLASSES)


class RegisterForm(StyledFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ('phone', 'first_name', 'email')
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'Votre numéro de téléphone'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Votre prénom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Votre email (pour récupérer le mot de passe)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True


class LoginForm(StyledFormMixin, AuthenticationForm):
    pass


class ChangePasswordForm(StyledFormMixin, PasswordChangeForm):
    pass


class ResetPasswordForm(StyledFormMixin, PasswordResetForm):
    pass


class ResetPasswordConfirmForm(StyledFormMixin, SetPasswordForm):
    pass
