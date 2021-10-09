from django.core import serializers
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import HttpResponse, redirect, render
from rest_framework import generics
from .serializers import PostSerializer
from .models import Post, Author
from .form import PostForm
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
def HomeView(request):
    template_name = 'LinkedSpace/Posts/posts.html'
    return render(request, template_name)

def post(request, post_id):
    return HttpResponse("You're looking at post %s." % post_id)

def add_Post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.author_id = request.user
            a.author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
            a.id = request.user.id + '/posts/' + a.post_pk
            a.comments_id = a.id + "/comments"
            a.published = timezone.now()
            a.save()

            return redirect(postListView)
        else:
            print(form.errors)
    else:
        form = PostForm()
    return render(request, "LinkedSpace/Posts/add_post.html", {'form': form})



class postList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    http_method_names = ['get']
    serializer_class = PostSerializer

postListView = postList.as_view()

# @api_view(['GET'])
# def postList(request):

#     posts = Post.objects.all()
#     http_method_names = ['get']
#     serializer = PostSerializer(posts, many=True)

#     response_dict = {
#         "type": "post",
#         "items": serializer.data
#     }

#     return Response(response_dict)
