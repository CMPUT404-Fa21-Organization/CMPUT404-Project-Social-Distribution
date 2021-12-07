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
from django.urls.conf import path, re_path
from Posts.views import *
from Posts.commentView import *

urlpatterns = [
    # All the NON-API Views
    path('', UserStreamView, name='user-stream-view'),
    path('connection/', ForeignPostsFrontend, name='foreign-posts-view'),
    path('connection/newLike/', newLike, name='foreign-posts-view-like'),
    path('connection/<team_pk>/<post_pk>/addcomment', ForeignPostsComment, name='foreign-posts-comment'),
    path('local/', LocalPosts, name='local-posts-view'),
    path('local/newLike/', newLike, name='local-posts-view-like'),
    path('newLike/', newLike, name='add-like'),
    path('manage/', ManagePostsList, name='posts-manage'),
    path('add_post/', newPost, name='add_post'),
    path('add_post/<auth_pk>', PrivatePostView, name='add_private_post'),
    path('edit/<post_pk>/', edit_Post, name='edit_Post'),
    path('delete/<post_pk>/', delete_Post, name='delete_Post'),
    path('<post_pk>/add_comment/', add_Comment, name='add_comment'),
    path('<post_pk>/', PostDetailView, name= 'post-detail-view'),
    path('<post_pk>/newLike/', newLike, name= 'add-like-post'),
    path('<post_pk>/comments/', AllCommentsList, name='comment-list'),
    path('<post_pk>/comments/newLike/', newLike, name='add-like-comment'),
    path('share/<post_pk>/', PostShare, name='post_share'),
]
