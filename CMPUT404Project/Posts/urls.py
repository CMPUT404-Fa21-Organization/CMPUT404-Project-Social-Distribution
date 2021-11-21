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
from .views import *
from .commentView import *

urlpatterns = [
    path('', PostsList, name='postsHome'),
    path('add_post/', PostsList, name='add_post'),
    path('manage/', ManagePostsList, name='posts-manage'),
    path('<post_pk>/', PostDetail, name='post'),
    path('<post_pk>/add_post/', PostDetail, name='add_post'),
    path('<post_pk>/add_comment/', add_Comment, name='add_comment'),
    path('<post_pk>/comment/', commentListView, name='comment'),
    path('<post_pk>/likes/', commentListView, name='comment')
]
