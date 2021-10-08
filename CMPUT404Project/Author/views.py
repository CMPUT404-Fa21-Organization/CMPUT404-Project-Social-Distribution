from django.shortcuts import HttpResponse, render
from Posts.models import *
from .serializers import AuthorSerializer, InboxSerializer
from .models import Author, Inbox

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
def authorHome(request):
    template_name = 'LinkedSpace/Author/author.html'
    return render(request, template_name)

def author(request, author_id):
    return HttpResponse("You're looking at author %s." % author_id)

@api_view(['GET'])
def authorsList(request):

    authors = Author.objects.all()
    serializer = AuthorSerializer(authors, many=True)

    response_dict = {
        "type": "authors",
        "items": serializer.data
    }

    return Response(response_dict)

@api_view(['GET'])
def authorDetail(request, id):

    authors = Author.objects.get(id=id)
    serializer = AuthorSerializer(authors, many=False)

    return Response(serializer.data)

@api_view(['PUT'])
def authorCreate(request):

    serializer = AuthorSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['POST'])
def authorUpdate(request, id):

    author = Author.objects.get(id=id)
    serializer = AuthorSerializer(instance=author, data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['GET'])
def authorInbox(request, id):
    author = Inbox.objects.get(author=id)
    serializer = InboxSerializer(author, many=False)

    return Response(serializer.data)

@api_view(['POST'])
def authorInboxUpdate(request, id):

    author = Inbox.objects.get(author=id)
    serializer = InboxSerializer(instance=author, data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)