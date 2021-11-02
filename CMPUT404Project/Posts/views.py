from django.core import serializers
from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import redirect, render
from django.views.generic.base import RedirectView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PostSerializer
from .models import Post, Author
from .form import PostForm
import json
import uuid
import re
import uuid
import re

# Create your views here.
# TODO Better CSS for Stream
# Non API view, Displays the users posts and github activity
def MyStreamView(request):
    # TODO Add Github API stuff here
    # TODO only display public posts if user not authenticated
    
    if(request.user.is_authenticated):
        author = request.user
        postsObjects = Post.objects.filter(author_id=author.pk)

    else:
        author = None
        postsObjects = Post.objects.all()

    posts = PostSerializer(postsObjects, many=True)
    
    for post in posts.data:
        post["isImage"] = False
        if(post["content"][:2] == "b'"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata
            

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

        if contentType in ["application/app", "image/png", "image/jpeg",]: 
            content = request.FILES['file'].read() #Inputfile
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
        comments_id = id + "/comments"

        posts = Post(pk=uid, id=id, author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, contentType=contentType, count=0, size=10, categories=categories,visibility=visibility, unlisted=unlisted, published=published, content=content, comments=comments_id)
        posts.save()
        print(request.data)
        print(func)

        if func == PostsList:
            print('PostsList')
            return redirect(func)
        else:
            print('PostDetail')
            return redirect(func, request.user.pk, uid)

    else:
        print(form.errors)
        form = PostForm()
        context = {'form': form, 'user':request.user, 'method':'PUT'}
        return render(request, "LinkedSpace/Posts/add_post.html", context)


@api_view(['GET', 'POST',])
def PostsList(request, auth_pk=None):
    if request.method == 'GET':
        print('PostsList GET')
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
        print('PostsList POST')
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
        print(request.get_full_path().split(' ')[0].split('/')[-3])
        uid = request.get_full_path().split(' ')[0].split('/')[-3]
        # return redirect(PostDetail, request.user.pk, uid)
        return newPost(request, PostDetail, uid)

    elif request.method == 'DELETE':
        post = Post.objects.get(pk=post_pk)
        if post.author_id_id == request.user.pk:
            post.delete()
        return redirect('delete_post', post_pk)

    elif request.method == 'POST':
        pass


@api_view(['GET',])
def ManagePostsList(request):

    posts = Post.objects.all().order_by('-published')
    

    return render(request, "LinkedSpace/Posts/manage_posts.html", {'posts': posts})