
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
from django.urls import path
from django.urls.conf import include
from .api import *
from .views import *

urlpatterns = [
 
    path('<auth_pk>/', AuthorDetailAPIView),
    path('<auth_pk>/followers', APIGetFollowers),
    path('<auth_pk>/followers/<fr_auth_pk>', ForeignAuthorAPI),
    path('<auth_pk>/posts/', include('Posts.urlsAPI')),
    path('<auth_pk>/inbox/', AuthorInboxView, name='author-inbox'),
    path('<auth_pk>/liked/', AuthorLikedView, name='author-liked-view')
    # DEPRECATED
    # path('<auth_pk>/inbox/', AuthorInboxView.as_view(), name='author-inbox'),
    # path('<auth_pk>/delete', AuthorDeleteView, name='author-delete'),

]
