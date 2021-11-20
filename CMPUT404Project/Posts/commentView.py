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


@api_view(['GET',])
def commentDetail(request, post_pk, comment_pk, auth_pk=None):
    comment = Comments.objects.get(pk=comment_pk)
    serializer = CommentSerializer(comment, many=False)
    return Response(serializer.data)

@api_view(['GET','POST'])
def commentListView(request, post_pk, auth_pk=None):
    if request.method == 'GET':
        if request.get_full_path().split(' ')[0].split('/')[-2] == 'add_comment':
            form = CommentForm()
            path =  request.get_full_path()[:-9]
            context = {'form': form, 'name':request.user.displayName, 'method':'POST', 'path':path}
            return render(request, "LinkedSpace/Posts/add_comment.html", context)
        else:
            if post_pk != None:
                comment = Comments.objects.filter(Post_pk=post_pk)
            else:
                comment = Comments.objects.all()
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
            if contentType in ('app','png','jpeg','html'):
                content = request.FILES['file'].read()
            else:
                content = form.cleaned_data["text"]

            author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'displayName', 'github',)))[0]['fields']

            post = Post.objects.get(pk = post_pk)
            #print(getattr(post, 'comments'), type(getattr(post, 'comments')))

            if uid == None:
                r_uid = uuid.uuid4().hex
                uid = re.sub('-', '', r_uid)
            id = getattr(post, 'comments') + uid
            #print(id)
            #input()
            comments = Comments(pk=uid, id=id, author=author, size=10, published=published, content=content)
            #print(comments.objects)
            comments.save()

            return redirect(commentListView, request.user.pk)
        else:
            print(form.as_table, '\n')
            print(form.errors)
    else:
        form = CommentForm()
    return render(request, "LinkedSpace/Posts/add_comment.html", {'form': form, 'user':request.user})