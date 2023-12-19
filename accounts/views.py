from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    is_staff = forms.BooleanField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'is_staff')

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'