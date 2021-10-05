"""CMPUT404Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from . import views
from Author.views import authorsList, authorCreate

urlpatterns = [
    path('', views.homeView, name='home'),
    path('login/', views.loginView, name='login'),
    path('authors/', views.authorsView, name='authorsView'),
    path('posts/',  include('Posts.urls')),
    path('author/', include('Author.urls')),



    # api stuff
    path('api/authors/', authorsList, name='authors-list'),
    # path('api/authors/', include('Author.urls')),
    path('api/author/', include('Author.urls')),
]