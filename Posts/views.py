from django.core import serializers
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render
from .commentModel import Comments
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PostSerializer
from Author.serializers import LikeSerializer
from Author.models import Inbox, Like, Liked, Followers
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

# Create your views here.
def newLike(request, auth_pk = None):
    # View to create a new like object after clicking the like button
    if request.user.is_authenticated:
        # TODO what is context supposed to be?
        context = request.POST["postID"] # "https://www.w3.org/ns/activitystreams"
        author = request.user
        object = request.POST["postID"]
        objectType = "post"
        if "comment" in object:
            objectType = "comment"
        post = Post.objects.get(id = object)
        postAuthor = Author.objects.get(email = post.author_id)
    
        summary = request.user.displayName + " liked " + postAuthor.displayName + "'s " + objectType
        if(Like.objects.filter(auth_pk = author, object = object).count() == 0):
            like = Like(context = context, auth_pk = author, object = object, summary = summary)
            like.save()

            # Send to inbox
            if author != postAuthor:
                inbox = Inbox.objects.get(auth_pk = postAuthor)
                inbox.iLikes.add(like)
        else:
            like = Like.objects.filter(auth_pk = author, object = object)
            like.delete()

        if(request.POST["context"] == "stream"):
            return HttpResponseRedirect(reverse('user-stream-view', kwargs={ 'auth_pk': auth_pk }))
        else:
            return HttpResponseRedirect(reverse('author-inbox-frontend'))

    else:
        return HttpResponseRedirect(reverse('login'))


# TODO Better CSS for Stream
# Non API view, Displays the users posts and github activity
def UserStreamView(request, auth_pk):
    # TODO Add Github API stuff here
    
    if(request.user.is_authenticated and request.user.pk == auth_pk):
        author = request.user
        postsObjects = Post.objects.filter(author_id=author.pk) # | Post.objects.filter(visibility = "PUBLIC")

    else:
        # TODO Friend Posts in stream
        author = Author.objects.get(pk = auth_pk)
        postsObjects = Post.objects.filter(author_id=author.pk, visibility = "PUBLIC")
    
    postsObjects = postsObjects.order_by('-published')

    posts = PostSerializer(postsObjects, many=True)
    
    # If Content is image
    for post in posts.data:
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata

    # Like Stuff
    # Calculte Number of Likes for Posts
    likeObjects = Like.objects.all()  
    likes = LikeSerializer(likeObjects,  many=True)   
    for post in posts.data:
        post["userLike"] = False
        post["numLikes"] = 0
        for like in likes.data:
            if post["id"] == like["object"]:
                post["numLikes"] += 1
    
    # Check which posts the user has already liked
    if(request.user.is_authenticated):
        likeObjects = Like.objects.filter(auth_pk = author)  
        userLikes = LikeSerializer(likeObjects,  many=True) 
        for post in posts.data:
            for like in userLikes.data:
                if post["id"] == like["object"]:
                    post["userLike"] = True

            

    context = {'posts':posts.data, 'user':author}

    template_name = 'LinkedSpace/Posts/posts.html'
    return HttpResponse(render(request, template_name, context),status=200)


def newPost(request, func, uid=None):
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

        source = ""
        origin = ""
        author_id = request.user
        print(json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',))))
        print("========================")
        author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'displayName', 'url', 'github',)))[0]['fields']
        published = timezone.now()

        if uid == None:
            r_uid = uuid.uuid4().hex
            uid = re.sub('-', '', r_uid)
        id = request.user.id + '/posts/' + uid
        comments_id = id + "/comment/"

        posts = Post(pk=uid, id=id, author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, contentType=contentType, count=0, size=10, categories=categories,visibility=visibility, unlisted=unlisted, published=published, content=content, comments=comments_id)
        posts.save()
        path = request.get_full_path().split('/')

        if func == PostsList:
            if len(path) > 4:
                return HttpResponseRedirect(reverse("postsHome", args=[path[2]]))
            else:
                return HttpResponseRedirect(reverse("postsHome"))
        else:
            if len(path) > 4:
                return HttpResponseRedirect(reverse("post", args=[uid, path[2],]))
            else:
                return HttpResponseRedirect(reverse("post", args=[uid,]))
    else:
        print(form.errors)
        form = PostForm()
        context = {'form': form, 'user':request.user, 'method':'PUT'}
        return render(request, "LinkedSpace/Posts/add_post.html", context)

"""
def deletePost(request, auth_pk, post_pk):
    post = Post.objects.get(pk=post_pk)
    if post.author_id_id == request.user.pk:
        comments = Comments.objects.filter(post_pk_str=post_pk)
        print(comments)
        print("")
        print(comments.id)
        input()
        for comment in comments:
            comment.delete()
        post.delete()
    request.method = 'GET'
    return HttpResponseRedirect(reverse("postsHome", args=[auth_pk,]))
"""


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
def PostsList(request, auth_pk=None):
    if request.method == 'GET':
        if request.get_full_path().split(' ')[0].split('/')[-2] == 'add_post':
            form = PostForm()
            path =  request.get_full_path()[:-9]
            context = {'form': form, 'name':request.user.displayName, 'method':'POST', 'path':path}
            return render(request, "LinkedSpace/Posts/add_post.html", context)
        else:
            if auth_pk != None:
                post = Post.objects.filter(author_id=auth_pk)
            else:
                post = Post.objects.all()
            serializer = PostSerializer(post, many=True)

            return Response(serializer.data)
    elif request.method == 'POST':
        return newPost(request, PostsList)

@api_view(['GET', 'POST', 'PUT', 'DELETE', ])
def PostDetail(request, post_pk=None, auth_pk=None):
    if request.method == 'GET':
        if request.get_full_path().split(' ')[0].split('/')[-2] == 'add_post':
            form = PostForm()
            path = request.get_full_path()[:-9]
            context = {'form': form, 'name':request.user.displayName, 'method':'PUT', 'path':path}
            return render(request, "LinkedSpace/Posts/add_post.html", context)
        else:
            post = Post.objects.filter(post_pk=post_pk)
            serializer = PostSerializer(post, many=True)

            return Response(serializer.data)

    elif request.method == 'PUT':
        print(request.get_full_path().split(' ')[0].split('/'))
        uid = request.get_full_path().split(' ')[0].split('/')[-3]
        return newPost(request, PostDetail, uid)

    elif request.method == 'DELETE':
        post = Post.objects.get(pk=post_pk)
        comments = Comments.objects.filter(Post_pk_str=post_pk)
        if post.author_id_id == request.user.pk:
            for comment in comments:
                comment.delete()
            post.delete()
        if auth_pk != None:
            post = Post.objects.filter(author_id=auth_pk)
        else:
            post = Post.objects.all()
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        uid = request.get_full_path().split(' ')[0].split('/')[-3]
        return newPost(request, PostDetail, uid)


@api_view(['GET',])
def ManagePostsList(request):
    posts = Post.objects.filter(author_id=request.user).order_by('-published')
    # posts = Post.objects.all().order_by('-published')
    
    return render(request, "LinkedSpace/Posts/manage_posts.html", {'posts': posts})