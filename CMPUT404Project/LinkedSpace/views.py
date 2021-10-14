from django import forms
from django.db.models import manager
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from Author.forms import CreateAuthorForm

from django.contrib.auth import authenticate, login, logout
from .models import *
from Author.models import AuthorManager, Author

# Create your views here.
def homeView(request):
    template_name = 'LinkedSpace/home.html'
    return render(request, template_name)

def loginView(request):
    template_name = 'LinkedSpace/login.html'

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email = email, password = password)
        
        if user:
            login(request, user)
            return redirect('home')
        

    return render(request, template_name)

def logoutView(request):
    logout(request)
    return redirect('login')

def registerView(request):
    template_name = 'LinkedSpace/register.html'
    form = CreateAuthorForm()

    if request.method == 'POST':
        form = CreateAuthorForm(request.POST)
        

        # TODO: Create a is_valid method for Author?
        if form.is_valid():
            user = Author.objects.create_user(displayName=form.cleaned_data.get('displayName'), email=form.cleaned_data.get('email'), password=form.cleaned_data.get('password1'))
            return redirect('login')
        


    context = {'form':form}
    return render(request, template_name, context)

def authorsView(request):
    template_name = 'LinkedSpace/authors.html'
    return render(request, template_name)
