"""Модуль с формами."""
from django import forms


class AuthRegForm(forms.Form):
    """Форма для регистрации и авторизации."""

    email = forms.EmailField(required=True, max_length=50)
    password = forms.CharField(required=True, min_length=8, max_length=50)

    def clean_email(self) -> str:
        """Приведение email к нижнему регистру."""
        return self.cleaned_data["email"].lower()





