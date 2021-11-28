from django.conf import settings
from django.core import serializers
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from requests import get
from .serializers import PostSerializer
from Author.serializers import LikeSerializer
from Author.models import Like
from .models import Post, Author
from .form import PostForm
import json
import uuid
import re
import uuid
import re
import base64
from django.db.models import Q
import django.core
from permissions import CustomAuthentication, AccessPermission
from django.core.paginator import Paginator

def newPost(request, uid=None, auth_pk=None):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        title = form.cleaned_data['title']
        descirption = form.cleaned_data['description']
        categories = form.cleaned_data['categories']
        visibility = form.cleaned_data['visibility']
        unlisted = form.cleaned_data['unlisted']
        contentType = form.cleaned_data['contentType']

        if contentType == "application/app": 
            content = request.FILES['file'].read() #Inputfile
        elif contentType in ["image/png", "image/jpeg",]:
            content = base64.b64encode(request.FILES['file'].read()) #Inputfile
        else:
            content = form.cleaned_data["text"]

        source = settings.SERVER_URL + "/"
        origin = settings.SERVER_URL + "/"

        author_id = Author.objects.get(pk=auth_pk)
        id = author_id.url
        author = json.loads(serializers.serialize('json', Author.objects.filter(pk=auth_pk), fields=('type', 'id', 'host', 'displayName', 'url', 'github',)))[0]['fields']

        if uid == None:
            r_uid = uuid.uuid4().hex
            uid = re.sub('-', '', r_uid)
        id = id + '/posts/' + uid + "/"
        comments_id = id + "comments/"

        published = timezone.now()

        posts = Post(pk=uid, id=id, author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, contentType=contentType, count=0, size=10, categories=categories,visibility=visibility, unlisted=unlisted, published=published, content=content, comments=comments_id)
        posts.save()
    else:
        print(request.data)
        print(form.errors)
        print(form.data)


@api_view(['GET',])
def PostLikesView(request, post_pk, auth_pk):
    post = Post.objects.get(post_pk = post_pk)
    author = Author.objects.get(pk = auth_pk)
    likeObjs = Like.objects.filter(~Q(auth_pk = author), object = post.id)

    Likes = LikeSerializer(likeObjs, read_only=True, many=True)
    likes = []
    for l in Likes.data:
        like = {}
        for key in l:
            if(key != "context"):
                like[key] = l[key]
        like["@context"] = l["context"]
        like["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=l["author"]), fields=('type', 'id', 'displayName', 'host', 'url', 'github',)))[0]['fields']
        likes.append(like)

    return Response(likes)


@api_view(['GET', 'POST',])
@authentication_classes([CustomAuthentication])
@permission_classes([AccessPermission])
def PostsList(request, auth_pk=None):
    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 5

    if request.method == 'GET':
        posts = Post.objects.all()
        paginator = Paginator(posts, page_size)
        page_obj = paginator.get_page(page_number)
        serializer = PostSerializer(page_obj.object_list, many=True)

    elif request.method == 'POST':
        newPost(request, auth_pk=request.data['auth_pk'])
        post = Post.objects.last()
        serializer = PostSerializer(post)

    return Response(serializer.data)

@api_view(['GET', 'POST', 'PUT', 'DELETE', ])
@authentication_classes([CustomAuthentication])
@permission_classes([AccessPermission])
def PostDetail(request, post_pk, auth_pk=None):
    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 5

    if request.method == 'GET':
        try:
            code = status.HTTP_200_OK
            post = Post.objects.get(post_pk=post_pk)
            serializer = PostSerializer(post)
        except Exception as e:
            print(e)
            code = status.HTTP_404_NOT_FOUND

            post = Post.objects.all()
            paginator = Paginator(post, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = PostSerializer(page_obj.object_list, many=True)

    elif request.method == 'POST':
        try:
            code = status.HTTP_200_OK
            post = Post.objects.get(post_pk=post_pk)
            if 'title' in request.data.keys():
                post.title = request.data['title']
            if 'description' in request.data.keys():
                post.description = request.data['description']
            if 'categories' in request.data.keys():
                post.categories = request.data['categories']
            if 'visibility' in request.data.keys():
                post.visibility = request.data['visibility']
            if 'unlisted' in request.data.keys():
                post.unlisted = request.data['unlisted']
            if 'contentType' in request.data.keys():
                post.contentType = request.data['contentType']
            if 'text' in request.data.keys():
                post.content = request.data['text']
            post.save()
            serializer = PostSerializer(post)
        except Exception as e:
            print(e)
            code = status.HTTP_400_BAD_REQUEST

            post = Post.objects.all()
            paginator = Paginator(post, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = PostSerializer(page_obj.object_list, many=True)

    elif request.method == 'PUT':
        try:
            code = status.HTTP_200_OK
            newPost(request, post_pk, request.data['auth_pk'])
            post = Post.objects.get(post_pk=post_pk)
            serializer = PostSerializer(post)
        except Exception as e:
            print(e)
            code = status.HTTP_400_BAD_REQUEST

            post = Post.objects.all()
            paginator = Paginator(post, page_size)
            page_obj = paginator.get_page(page_number)
            serializer = PostSerializer(page_obj.object_list, many=True)

    elif request.method == 'DELETE':
        try:
            post = Post.objects.get(post_pk=post_pk)
            post.delete()
            code = status.HTTP_200_OK
        except Exception as e:
            print(e)
            code = status.HTTP_404_NOT_FOUND

        post = Post.objects.all()
        paginator = Paginator(post, page_size)
        page_obj = paginator.get_page(page_number)
        serializer = PostSerializer(page_obj.object_list, many=True)

    return Response(serializer.data, code)

@api_view(['GET',])
def connection(request, auth_id=None):
    data = []

    team3 = get('https://social-dis.herokuapp.com/posts', auth=('socialdistribution_t03','c404t03'))
    if team3.status_code == 200:
        data.append(team3.json())

    team15 = get('https://unhindled.herokuapp.com/service/allposts/', auth=('connectionsuperuser','404connection'))
    if team15.status_code == 200:
        data.append(team15.json())

    team17 = get('https://cmput404f21t17.herokuapp.com/service/connect/public/', auth=('4cbe2def-feaa-4bb7-bce5-09490ebfd71a','123456'))
    if team17.status_code == 200:
        data.append(team17.json())

    return Response({'connection': data})