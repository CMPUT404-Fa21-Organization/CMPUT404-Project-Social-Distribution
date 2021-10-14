from django.core import serializers
from django.utils import timezone
from django.shortcuts import HttpResponse, redirect, render
from rest_framework import generics
from .serializers import PostSerializer
from .models import Post, Author
from .form import PostForm
import json

# Create your views here.
def HomeView(request):
    template_name = 'LinkedSpace/Posts/posts.html'
    return render(request, template_name)

def post(request, post_id):
    return HttpResponse("You're looking at post %s." % post_id)

def add_Post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            source = form.cleaned_data['source']
            origin = form.cleaned_data['origin']
            descirption = form.cleaned_data['description']
            visibility = form.cleaned_data['visibility']
            unlisted = form.cleaned_data['unlisted']

            author_id = request.user
            author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
            published = timezone.now()
            content = request.FILES['file'].read() #Inputfile
            # content = 'text plain'

            posts = Post(author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, count=0, size=10, visibility=visibility, unlisted=unlisted, published=published, content=content)

            id = request.user.id + '/posts/'
            posts.id = id + posts.pk
            comments_id = posts.id + "/comments"
            posts.comments = comments_id
            comments = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
            posts.save()

            return redirect(postListView)
        else:
            print(form.as_table, '\n')
            print(form.errors)
    else:
        form = PostForm()
    return render(request, "LinkedSpace/Posts/add_post.html", {'form': form, 'user':request.user.id})

class postList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    http_method_names = ['get']
    serializer_class = PostSerializer

postListView = postList.as_view()
