from django.core import serializers
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import HttpResponse, render
from .serializers import PostSerializer
from .models import Post, Author
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
        a = form.save(commit=False)
        a.author_id = "85441b95489243e98b6e87a3d574b072"
        a.author = serializers.serialize('json', Author.objects.filter(email="xinjian@ualerta.ca"))
        a.published = timezone.now()
        a.save()
        # form['author_id'] = "http://127.0.0.1:8000/author/7bdc85a97b354cceb03e38422449758e"
        # form['author'] = {
        #                 "type": "author",
        #                  "id": "http://127.0.0.1:8000/author/7bdc85a97b354cceb03e38422449758e",
        #                  "host": "http://127.0.0.1:8000/",
        #                  "url": "http://127.0.0.1:8000/author/7bdc85a97b354cceb03e38422449758e",
        #                  "displayName": "King",
        #                  "github": ""
        #                  }
        # form['type'] = "post"
        # form['contentType'] = "text/markdown"
        # form['catergories'] = 'Web'
        # form['comments_id'] =  'comments', 'pulished',
        # form.save()
        # print(form.as_table())
        # print("\n\n", form.errors, "\n\n")
        # print("\n\n", form.is_valid(), "\n\n")
        # if form.is_valid():
        #     print("----------------------------------")

            
        #     title = form.cleaned_data['title']
        #     source = form.cleaned_data['source']
        #     origin = form.cleaned_data['origin']
        #     description = form.cleaned_data['description']
        #     count = form.cleaned_data['count']
        #     size = form.cleaned_data['size']

        #     visibility = form.cleaned_data['visibility']
        #     unlisted = form.cleaned_data['unlisted']
        #     # if unlisted == 'T':
        #     #     unlisted = True
        #     # else:
        #     #     unlisted = False


        #     # print(title, source, origin, description, size, count, visibility, unlisted)
        #     print(title)

        #     p = Post(id="http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072",
        #         author ={
        #                     "type": "author",
        #                     "id": "http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072",
        #                     "host": "http://127.0.0.1:8000/",
        #                     "url": "http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072",
        #                     "displayName": "belton",
        #                     "github": ""
        #                 },
        #          title=title,
        #          source =source,
        #          origin = origin,
        #          description=description,
        #          contentType = "text/plain",
        #          categories="web",
        #          size=size,
        #          count=count,
        #          comments=dict,
        #          published="2021-10-08T19:51:33.742891Z",
        #          visibility=visibility,
        #          unlisted=unlisted)
        #     p.save()

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
