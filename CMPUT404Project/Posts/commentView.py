from django.core import serializers
from django.utils import timezone
from django.shortcuts import redirect, render
import Posts
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CommentSerializer, PostSerializer
from .models import Post, Author
import json
from commentModel import *
from commentForm import *


@api_view(['GET',])
def comment(request, auth_pk, post_pk, comment_pk):
    comment = Comments.objects.get(pk=comment_pk)
    serializer = CommentSerializer(comment, many=False)
    return Response(serializer.data)

@api_view(['GET',])
def commentListView(request):
    comment = Comments.objects.all()
    serializer = PostSerializer(comment, many=True)
    return Response(serializer.data)

def add_Comment(request, auth_pk, post_pk):
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            size = form.cleaned_data['size']
            published = timezone.now()
            content = request.FILES['file'].read()
            
            author_id = request.user
            author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']

            comments = Comments(author_id=author_id, author=author, size=size, published=published, content=content)
            comment_id = Post.comments_id + '/' + Comments.pk 
            comments.save()

            return redirect(commentListView)
        else:
            print(form.as_table, '\n')
            print(form.errors)
    else:
        form = CommentForm()
    return render(request, "LinkedSpace/Posts/add_comment.html", {'form': form, 'user':request.user.id})