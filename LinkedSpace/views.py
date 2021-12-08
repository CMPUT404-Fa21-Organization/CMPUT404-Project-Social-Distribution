from django import forms
from django.db.models import manager
from django.shortcuts import redirect, render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from Author.forms import CreateAuthorForm
from Author.serializers import *
from django.urls import reverse
from django.contrib import messages

from Author.serializers import *

from django.contrib.auth import authenticate, login, logout
from .models import *
from Author.models import AuthorManager, Author, Followers, Inbox
from Author.forms import EditAuthorForm
from django.core.paginator import Paginator

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

def profileEdit(request):
    template_name = 'LinkedSpace/profile_edit.html'

    if request.method == "POST":
        form = EditAuthorForm(request.POST, instance=request.user)

        if form.is_valid():
            github_username = form.cleaned_data['github']
            displayName = form.cleaned_data['displayName']
            email = form.cleaned_data['email']

            request.user.github = "http://github.com/" + github_username
            request.user.displayName = displayName
            request.user.email = email

            form.save()
            messages.success(request, 'Profile updated successfully.', extra_tags='success')
            return HttpResponseRedirect('/profile/')
        else:
            messages.success(request, 'Profile could not be updated.', extra_tags='failure')
            return HttpResponseRedirect('/profile/')
    else:
        form = EditAuthorForm(instance=request.user)
        git_url = request.user.github
        displayName = request.user.displayName
        email = request.user.email

        gituser = git_url.replace("http://github.com/", "")
        context = {'form':form, 'github_username':gituser, 'displayName':displayName, 'email':email}
        
        return HttpResponse(render(request, template_name, context),status=200)
    
    return HttpResponse(render(request, 'LinkedSpace/profile.html'),status=200)

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
            return redirect(homeView)
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

            return redirect(loginView)
            return HttpResponseRedirect('/login')

    context = {'form':form}
    return render(request, template_name, context)

def authorsView(request):
    template_name = 'LinkedSpace/authors.html'

    authorObjects = Author.objects.filter(id__icontains = "linkedspace-staging") | Author.objects.filter(id__icontains = "127.0.0.1")

    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 10

    paginator = Paginator(authorObjects, page_size)
    page_obj = paginator.get_page(page_number)

    context = {'Authors':page_obj}

    return HttpResponse(render(request, template_name, context),status=200)
