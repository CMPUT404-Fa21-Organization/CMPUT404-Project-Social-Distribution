from django.http.response import HttpResponseRedirect
from django.shortcuts import HttpResponse, render, redirect
from .serializers import PostSerializer
from .models import Post
from .form import PostForm

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
def HomeView(request):
    template_name = 'LinkedSpace/Posts/posts.html'
    return render(request, template_name)

def post(request, post_id):
    return HttpResponse("You're looking at post %s." % post_id)

def add_Post(request):
    print(request)
    if request.method == "POST":
        form = PostForm(request.POST)
        print(form, form.as_table(), form.is_valid())
        if form.is_valid():
            print("----------------------------------")

            
            title = form.cleaned_data('title')
            source = form.cleaned_data('source')
            origin = form.cleaned_data('origin')
            description = form.cleaned_data('description')
            count = form.cleaned_data('count')
            size = form.cleaned_data('size')

            visibility = form.cleaned_data('visibility')
            unlisted = form.cleaned_data('unlisted')


            # print(title, source, origin, description, size, count, visibility, unlisted)
            print(title)

            p = Post(id="http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072",
                author ={
                            "type": "author",
                            "id": "http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072",
                            "host": "http://127.0.0.1:8000/",
                            "url": "http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072",
                            "displayName": "belton",
                            "github": ""
                        },
                 title=title,
                 source =source,
                 origin = origin,
                 description=description,
                 contentType = "text/plain",
                 categories="web",
                 size=size,
                 count=count,
                 Comments="",
                 published="2021-10-08T19:51:33.742891Z",
                 visibility=visibility,
                 unlisted=unlisted)
            p.save()

            return HttpResponseRedirect('LinkedSpace/Posts/posts.html')
    else:
        form = PostForm()
    return render(request, "LinkedSpace/Posts/add_post.html", {'form': form})

@api_view(['GET'])
def postList(request):

    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)

    response_dict = {
        "type": "post",
        "items": serializer.data
    }

    return Response(response_dict)
