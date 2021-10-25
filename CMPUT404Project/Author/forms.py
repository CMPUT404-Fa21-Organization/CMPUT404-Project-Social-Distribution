from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import AuthorManager, Author

class CreateAuthorForm(UserCreationForm):
    class Meta:
        model = Author
        fields = ['displayName','email', 'password1', 'password2', 'github']

    displayName= forms.CharField(max_length=100,
                           widget= forms.TextInput
                           (attrs={'class':'form-control'}))

    email= forms.CharField(max_length=100,
                           widget= forms.EmailInput
                           (attrs={'class':'form-control'}))

    password1 = forms.CharField(max_length=100,
                           widget= forms.PasswordInput
                           (attrs={'class':'form-control'}))

    password2 = forms.CharField(max_length=100,
                           widget= forms.PasswordInput
                           (attrs={'class':'form-control'}))

    github = forms.CharField(max_length=100,
                           widget= forms.TextInput
                           (attrs={'class':'form-control'}))

