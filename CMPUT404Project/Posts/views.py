from django.shortcuts import HttpResponse, render
from .serializers import PostSerializer
from .models import Post

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
def HomeView(request):
    template_name = 'LinkedSpace/Posts/posts.html'
    return render(request, template_name)

def post(request, post_id):
    return HttpResponse("You're looking at post %s." % post_id)

@api_view(['GET'])
def postList(request):

    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)

    response_dict = {
        "type": "post",
        "items": serializer.data
    }

    return Response(response_dict)
