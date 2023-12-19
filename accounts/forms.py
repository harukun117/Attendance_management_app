from django import forms
from django.contrib.auth.models import User

class CustomSignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    is_staff = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'is_staff']
