from django import forms
from django.db.models import manager
from django.shortcuts import redirect, render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from Author.forms import CreateAuthorForm
from Author.serializers import *
from django.urls import reverse
from django.contrib import messages

from Author.serializers import *

from django.contrib.auth import authenticate, login, logout
from .models import *
from Author.models import AuthorManager, Author

# Create your views here.
def homeView(request):
    template_name = 'LinkedSpace/home.html'
    return render(request, template_name)

def profileView(request):
    template_name = 'LinkedSpace/profile.html'

    user = Author.objects.get(email = request.user.email)
    context = {'user':user}
    return HttpResponse(render(request, template_name, context),status=200)

def loginView(request):
    template_name = 'LinkedSpace/login.html'
    serializer_class = AuthorLoginSerializer
    
    if request.method == 'POST':

        # serializer = serializer_class(data=request.data,
        #                                    context={'request': request})
        # serializer.is_valid(raise_exception=True)
        
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email = email, password = password)
        
        if user:
            login(request, user)
            return HttpResponse(render(request, 'LinkedSpace/home.html'),status=200)

        else:
            messages.error(request, 'Please enter a valid email and password. Note that both fields are case sensitive.')
            return HttpResponse(render(request, 'LinkedSpace/login.html'),status=401)
        

    return render(request, template_name)

def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))
    # return HttpResponse(render(request,'LinkedSpace/login.html'),status=200)

def registerView(request):
    
    template_name = 'LinkedSpace/register.html'
    form = CreateAuthorForm()

    serializer_class = AuthorRegisterSerializer

    if request.method == 'POST':
        form = CreateAuthorForm(request.POST)
        
        if form.is_valid():
            user = Author.objects.create_user(displayName=form.cleaned_data.get('displayName'), email=form.cleaned_data.get('email'), password=form.cleaned_data.get('password1'), github=form.cleaned_data.get('github'))
            return HttpResponse(render(request, 'LinkedSpace/login.html'),status=200)
        
        

    context = {'form':form}
    return render(request, template_name, context)

def authorsView(request):
    template_name = 'LinkedSpace/authors.html'
    return render(request, template_name)
