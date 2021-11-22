from django.core import serializers
from django.utils import timezone
from django.shortcuts import redirect, render, get_object_or_404
from rest_framework.decorators import api_view
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
"""
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
                #print("second")
                #print(post_pk, type(post_pk))
                comment = Comments.objects.filter(Post_pk_str=post_pk)
            else:
                comment = Comments.objects.all()
                print("third")
            serializer = CommentSerializer(comment, many=True)

            return Response(serializer.data)
    elif request.method == 'POST':
        return add_Comment(request, commentListView)

def add_Comment(request, post_pk, auth_pk=None, uid=None):
    if request.method == "POST":
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
            author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'displayName', 'github',)))[0]['fields']
            auth_pk = author["id"].split("/")[-1]
            post = Post.objects.get(pk = post_pk)
            #print("add_comment post_pk: ", post_pk)
            post_pk_str = getattr(post, 'post_pk')

            if uid == None:
                r_uid = uuid.uuid4().hex
                uid = re.sub('-', '', r_uid)
            id = getattr(post, 'comments') + uid
            #print(id)
            #input()
            comments = Comments(pk=uid, id=id, Post_pk_str = post_pk_str, auth_pk_str = auth_pk, author=author, size=10, published=published, content=content)
            #print(comments.objects)
            comments.save()
            #print("user.pk ", request.user.pk)
            return redirect(commentListView, post_pk_str)
        else:
            print(form.as_table, '\n')
            print(form.errors)
    else:
        form = CommentForm()
    return render(request, "LinkedSpace/Posts/add_comment.html", {'form': form, 'user':request.user})