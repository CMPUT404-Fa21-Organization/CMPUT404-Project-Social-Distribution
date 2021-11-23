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
from django.contrib import admin
from django.urls.conf import include, path
from Author.views import *
from LinkedSpace.views import *
from Posts.views import *
from GitEvents.views import *
from Posts.commentView import *

urlpatterns = [
    # All the NON-API Views
    path('', homeView, name='home'),
    path('login/', loginView, name='login'),
    path('register/', registerView, name='register'),
    path('logout/', logoutView, name='logout'),
    path('profile/', profileView, name='author-detail'),
    

    path('inbox/', MyInboxView, name='author-inbox-frontend'),
    path('inbox/clearInbox/', clearInbox, name='clear-inbox'),
    path('inbox/newLike/', newLike, name='add-like'),
    path('inbox/acceptFollow/', acceptFollow, name='accept-follow'),

    path('author/<auth_pk>/posts/', UserStreamView, name='user-stream-view'),
    path('author/<auth_pk>/posts/newLike/', newLike, name='add-like'),
    
    path('git/', include('GitEvents.urls')),

    path('posts/add_post/', PostsList, name='add_post'),
    path('posts/manage/', ManagePostsList, name='posts-manage'),
    path('posts/<post_pk>/add_comment/', add_Comment, name='add_comment'),

    # TODO Not sure if this is non-api
    path('author/', authorHome, name='authorHome'),

    # All the API views
    path('api/', include('LinkedSpace.urls')),

    # Django Admin Panel
    path('admin/', admin.site.urls),
]
