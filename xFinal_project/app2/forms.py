from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('brooder_manager', 'Brooder Manager'),
        ('sales_rep', 'Sales Rep'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ("username", "role", "password1", "password2")