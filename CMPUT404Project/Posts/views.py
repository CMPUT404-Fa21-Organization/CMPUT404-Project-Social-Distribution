from django.core import serializers
from django.utils import timezone
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PostSerializer
from .models import Post, Author
from .form import PostForm
import json

# Create your views here.
@api_view(['GET',])
def PostsList(request, auth_pk=None):
    if auth_pk != None:
        post = Post.objects.filter(author_id=auth_pk)
    else:
        post = Post.objects.all()
    serializer = PostSerializer(post, many=True)

    return Response(serializer.data)

@api_view(['GET',])
def PostDetail(request, post_pk, auth_pk=None):
    post = Post.objects.filter(post_pk=post_pk)
    serializer = PostSerializer(post, many=True)

    return Response(serializer.data)

def add_Post(request, auth_pk=None):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            source = form.cleaned_data['source']
            origin = form.cleaned_data['origin']
            descirption = form.cleaned_data['description']
            visibility = form.cleaned_data['visibility']
            unlisted = form.cleaned_data['unlisted']
            contentType = form.cleaned_data['contentType']
            print(contentType)
            if contentType in ["app", "png", "jpeg", "html"]: 
                content = request.FILES['file'].read() #Inputfile
            else:
                content = form.cleaned_data["text"]

            author_id = request.user
            author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
            published = timezone.now()

            posts = Post(author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, contentType=contentType, count=0, size=10, visibility=visibility, unlisted=unlisted, published=published, content=content)

            id = request.user.id + '/posts/'
            posts.id = id + posts.pk
            comments_id = posts.id + "/comments"
            posts.comments = comments_id
            # comments = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
            posts.save()

            return redirect(PostsList, request.user.pk)
        else:
            print(form.errors)
    else:
        form = PostForm()
    return render(request, "LinkedSpace/Posts/add_post.html", {'form': form, 'user':request.user})

# class postList(generics.ListCreateAPIView):
#     queryset = Post.objects.all()
#     http_method_names = ['get']
#     serializer_class = PostSerializer

# postListView = postList.as_view()
