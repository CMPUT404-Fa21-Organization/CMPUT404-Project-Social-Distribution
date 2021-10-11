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
from django.conf.urls import url
from django.urls import include, path
from . import views
from .views import *

urlpatterns = [

    path('', views.authorHome, name='authorHome'),
    path('<author>/inbox/', AuthorInboxView.as_view(), name='author-inbox'),
    # path('<auth_pk>/inbox/', views.authorInboxUpdate, name='author-inbox-update'),
    # CBVs
    path('login/', AuthorLoginView.as_view(), name='author-login'), # needs to be moved to main app
    path('register/', AuthorCreateView.as_view(), name='author-register'), # needs to be moved to main app
    path('<auth_pk>/', AuthorDetailView.as_view()),
    path('<auth_pk>/edit', AuthorProfileView.as_view(), name='author-udpate'),
]