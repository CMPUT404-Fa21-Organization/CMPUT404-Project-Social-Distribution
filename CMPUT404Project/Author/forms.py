from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import AuthorManager, Author

class CreateAuthorForm(UserCreationForm):
    class Meta:
        model = Author
        fields = ['displayName','email', 'password1', 'password2']
