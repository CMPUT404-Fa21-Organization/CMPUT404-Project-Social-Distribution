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
from .viewsAPI import *
from .commentView import *

urlpatterns = [
    path('', PostsList, name='postsHome'),
    path('connection/', connection, name='connection'),
    path('<post_pk>/', PostDetail, name='post'),
    path('<post_pk>/comments/', commentListView, name='comment'),
    path('<post_pk>/comments/<comment_pk>/', commentDetail, name='commentDet'),
    path('<post_pk>/likes/', PostLikesView, name='post-likes-view'),
    path('<post_pk>/comments/<comment_pk>/likes/', CommentLikesView, name='comment-likes-view'),
]
