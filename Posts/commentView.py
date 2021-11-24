from django.core import serializers
from django.utils import timezone
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CommentSerializer, PostSerializer
from .models import Post, Author
import json
from .commentModel import *
from .commentForm import *


@api_view(['GET',])
def commentDeatil(request, post_pk, comment_pk, auth_pk=None):
    comment = Comments.objects.get(pk=comment_pk)
    serializer = CommentSerializer(comment, many=False)
    return Response(serializer.data)

@api_view(['GET',])
def commentListView(request, post_pk, auth_pk=None):
    comment = Comments.objects.filter(post_pk=post_pk)
    serializer = CommentSerializer(comment, many=True)
    return Response(serializer.data)

def add_Comment(request, post_pk, auth_pk=None):
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

            post = Post.objects.get(pk=post_pk)
            print(getattr(post, 'pk'), type(getattr(post, 'pk')))
            #print(post[0]['id'], type(post[0]['id']))
            # print(request)
            input()
            comments = Comments(Post_pk=post.pk, author=author, size=10, published=published, content=content)

            comments.id = list(post)[0]["id"]+"/comments/"+ comments.pk
            comments.save()

            return redirect(commentListView, request.user.pk)
        else:
            print(form.as_table, '\n')
            print(form.errors)
    else:
        form = CommentForm()
    return render(request, "LinkedSpace/Posts/add_comment.html", {'form': form, 'user':request.user})