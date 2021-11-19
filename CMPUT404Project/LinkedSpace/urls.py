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

from Posts.views import MyStreamView
from . import views
from Posts.views import ManagePostsList, newLike
from Author.views import AuthorsListView, MyInboxView, acceptFollow


urlpatterns = [
    path('', views.homeView, name='home'),
    path('login/', views.loginView, name='login'),
    path('register/', views.registerView, name='register'),
    path('logout/', views.logoutView, name='logout'),
    path('authors/', AuthorsListView, name='authorsView'),
    path('profile/', views.profileView, name='author-detail'),
    path('posts/',  include('Posts.urls')),
    path('stream/', MyStreamView, name='user-stream-view'),
    path('author/', include('Author.urls')),
    path('git/', include('GitEvents.urls')),
    path('inbox/', MyInboxView, name='author-inbox-frontend'),
    path('inbox/acceptFollow/', acceptFollow, name='accept-follow'),
    path('stream/newLike/', newLike, name='add-like')
    # path('posts/',  include('Posts.urls')),
]
