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
from Author.models import AuthorManager, Author, Followers, Inbox

# Create your views here.
def homeView(request):
    template_name = 'LinkedSpace/home.html'
    return render(request, template_name)

def profileView(request):
    template_name = 'LinkedSpace/profile.html'

    if request.user.is_authenticated:

        user = Author.objects.get(email = request.user.email)
        git_username = user.github.replace("http://github.com/", "")
        context = {'user':user, 'git_username':git_username}
        return HttpResponse(render(request, template_name, context),status=200)

    else:
        return HttpResponse(render(request, 'LinkedSpace/login.html'),status=200)

# https://stackoverflow.com/questions/49553511/why-authenticate-return-none-for-inactive-users

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
            if not user.is_active:
                # print("This is NOT an active user.")
                messages.error(request, 'Account Activation Pending.', extra_tags='inactive')
                return HttpResponse(render(request, 'LinkedSpace/login.html'),status=401)
            else:
                login(request, user)
            return HttpResponse(render(request, 'LinkedSpace/home.html'),status=200)

        else:
            messages.error(request, 'Please enter a valid email and password. Note that both fields are case sensitive.', extra_tags='invalid')
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
            git_user = form.cleaned_data.get('github')
            github_url = f'http://github.com/{git_user}'
            user = Author.objects.create_user(displayName=form.cleaned_data.get('displayName'), email=form.cleaned_data.get('email'), password=form.cleaned_data.get('password1'), github=github_url)
            inbox = Inbox(auth_pk = user)
            followers = Followers(auth_pk = user)
            followers.save()
            inbox.save()
            
            return HttpResponseRedirect('/login')
            
            # return render(request,"my_blog/post_create.html",context)
        
        

    context = {'form':form}
    return render(request, template_name, context)

def authorsView(request):
    template_name = 'LinkedSpace/authors.html'
    return render(request, template_name)
