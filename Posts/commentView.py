from django.core import serializers
from django.utils import timezone
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .serializers import CommentSerializer, PostSerializer
from django.http.response import HttpResponse, HttpResponseRedirect
from .models import Post, Author
import json
from .commentModel import *
from .commentForm import *
import uuid
import re
import base64
from Author.models import *
from Author.serializers import *
import django.core
from django.db.models import Q
from permissions import CustomAuthentication, AccessPermission
from django.core.paginator import Paginator

@api_view(['GET',])
def CommentLikesView(request, comment_pk, post_pk, auth_pk):
    comment = Comments.objects.get(pk = comment_pk)
    author = Author.objects.get(pk = auth_pk)
    likeObjs = Like.objects.filter(~Q(auth_pk = author), object = comment.id)

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

"""
@api_view(['GET', 'POST', ])
def commentDetail(request, post_pk, comment_pk, auth_pk=None):
    if request.method == 'GET':
        if request.get_full_path().split(' ')[0].split('/')[-2] == 'add_comment':
            form = CommentForm()
            path = request.get_full_path()[:-9]
            context = {'form': form, 'name':request.user.displayName, 'method':'PUT', 'path':path}
            return render(request, "LinkedSpace/Posts/add_comment.html", context)
        else:
            print("get")
            comment = Comments.objects.get(pk=comment_pk)
            serializer = CommentSerializer(comment, many=False)
            return Response(serializer.data)

    elif request.method == 'PUT':
        print("put")
        #print(request.get_full_path().split(' ')[0].split('/'))
        uid = request.get_full_path().split(' ')[0].split('/')[-3]
        return add_Comment(request, commentDetail, post_pk, uid)

    elif request.method == 'DELETE':
        print("delete")
        comment = Comments.objects.get(pk=comment_pk)
        if getattr(comment, 'auth_pk_str') == request.user.pk:
            comment.delete()
        if auth_pk != None:
            comment = Comments.objects.filter(auth_pk_str=auth_pk)
        else:
            comment = Comments.objects.all()
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        uid = request.get_full_path().split(' ')[0].split('/')[-3]
        return add_Comment(request, commentDetail, uid)
"""
"""
@api_view(['GET','POST'])
def commentListView(request, post_pk, auth_pk=None):
    if request.method == 'GET':
        #print("request: ", request.get_full_path().split(' ')[0].split('/')[-2])
        if request.get_full_path().split(' ')[0].split('/')[-2] == 'add_comment':
            form = CommentForm()
            path =  request.get_full_path()[:-9]
            print("first")
            context = {'form': form, 'name':request.user.displayName, 'method':'POST', 'path':path}
            return render(request, "LinkedSpace/Posts/add_comment.html", context)
        else:
            if post_pk != None:
                print("second")
                #print(post_pk, type(post_pk))
                comment = Comments.objects.filter(Post_pk_str=post_pk)
                post = Post.objects.get(pk=post_pk)
                post_id = getattr(post, 'id')
                comment_id = getattr(post, 'comments')
                print(post_id, comment_id)
            else:
                comment = Comments.objects.all()
                #comment_id = getattr(comment, 'id')
                print("third")
            serializer = CommentSerializer(comment, many=True)

            response_dict = {
                "type": "comments",
                "page": "1",
                "size": "10",
                "post": post_id,
                "id": comment_id,
                "comments": serializer.data,
            }
            return Response(response_dict)
    elif request.method == 'POST':
        return add_Comment(request, commentListView)
"""

def add_Comment(request, post_pk, auth_pk=None, uid=None):
    if request.method == "POST":
        print("comment POST method")
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            published = timezone.now()
            contentType = form.cleaned_data['contentType']
            if contentType == "application/app": 
                content = request.FILES['file'].read() #Inputfile
            elif contentType in ["image/png", "image/jpeg",]:
                content = base64.b64encode(request.FILES['file'].read()) #Inputfile
            else:
                content = form.cleaned_data["text"]
            author = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'displayName', 'github',)))[0]['fields']
            auth_pk = author["id"].split("/")[-1]
            try:
                post = Post.objects.get(pk = post_pk)
                #print("add_comment post_pk: ", post_pk)
                post_pk_str = getattr(post, 'post_pk')

                if uid == None:
                    r_uid = uuid.uuid4().hex
                    uid = re.sub('-', '', r_uid)
                id = getattr(post, 'comments') + uid
                print("comment_id ",id)
                #input()
                comments = Comments(pk=uid, id=id, Post_pk=post, Post_pk_str = post_pk_str, auth_pk_str = auth_pk, author=author, size=10, published=published, content=content, contentType = contentType)
                #print(comments.objects)
                comments.save()
                #print("user.pk ", request.user.pk)
                print("redirecting to AllCommentsList")
                return redirect(AllCommentsList, post_pk_str)
            except:
                ## let the user know that the post does not exist * need  popup to let user know
                context = {'form': form, 'user':request.user, 'method':'GET'}
                return render(request, "LinkedSpace/home.html", context)
        else:
            print(form.as_table, '\n')
            print(form.errors)
    else:
        form = CommentForm()
    return render(request, "LinkedSpace/Posts/add_comment.html", {'form': form, 'user':request.user})

def AllCommentsList(request, post_pk, auth_pk = None):
    commentsObj = Comments.objects.filter(Post_pk_str=post_pk).order_by('-published')

    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 5

    comments = CommentSerializer(commentsObj, many = True)

    # If Content is image
    for post in comments.data:
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata

    # Like Stuff
    # Calculte Number of Likes for Posts
    likeObjects = Like.objects.all()  
    likes = LikeSerializer(likeObjects,  many=True)   
    for post in comments.data:
        post["userLike"] = False
        post["numLikes"] = 0
        for like in likes.data:
            if post["id"] == like["object"]:
                post["numLikes"] += 1
    
    # Check which posts the user has already liked
    if(request.user.is_authenticated):
        likeObjects = Like.objects.filter(auth_pk = request.user)  
        userLikes = LikeSerializer(likeObjects,  many=True) 
        for post in comments.data:
            for like in userLikes.data:
                if post["id"] == like["object"]:
                    post["userLike"] = True

    paginator = Paginator(comments.data, page_size)
    page_obj = paginator.get_page(page_number)
    print("redirected to comment list html")
    return render(request, "LinkedSpace/Posts/all_comment_list.html", {'comments': page_obj})