from rest_framework.decorators import api_view, authentication_classes, permission_classes
import requests
from rest_framework.response import Response
from .models import Author
from rest_framework import status
from .serializers import AuthorSerializer
from permissions import CustomAuthentication, AccessPermission
from django.core.paginator import Paginator


@api_view(['GET',])
@authentication_classes([CustomAuthentication])
@permission_classes([AccessPermission])
def AuthorsListAPIView(request):

    authors = Author.objects.filter(url__icontains = "linkedspace")

    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 5

    paginator = Paginator(authors, page_size)
    page_obj = paginator.get_page(page_number)

    serializer = AuthorSerializer(page_obj.object_list, many=True)

    response_dict = {
        "type": "authors",
        "items": serializer.data
    }

    return Response(response_dict)

@api_view(['GET', 'POST',])
@authentication_classes([CustomAuthentication])
@permission_classes([AccessPermission])
def AuthorDetailAPIView(request, auth_pk):
    try:
        author = Author.objects.get(pk=auth_pk)
    except Author.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = AuthorSerializer(instance=author)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        if 'displayName' in request.data.keys():
            author.displayName = request.data['displayName']
        if 'email' in request.data.keys():

            if not len(Author.objects.filter(email=request.data['email'])):
                author.email = request.data['email'] # update email field
            else:
                # email already exists
                serializer = AuthorSerializer(author)
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)      

        if 'github' in request.data.keys():
            github_user = request.data['github']
            author.github = f'http://github.com/{github_user}'

        author.save()
        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET',])
def AuthorsConnection(request, auth_id=None):
    data = []

    team3 = requests.get('https://social-dis.herokuapp.com/authors', auth=('socialdistribution_t03','c404t03'))
    if team3.status_code == 200:
        data.append(team3.json())

    team15 = requests.get('https://unhindled.herokuapp.com/service/authors/', auth=('connectionsuperuser','404connection'))
    if team15.status_code == 200:
        data.append(team15.json())

    team17 = requests.get('https://cmput404f21t17.herokuapp.com/service/connect/public/author/', auth=('4cbe2def-feaa-4bb7-bce5-09490ebfd71a','123456'))
    if team17.status_code == 200:
        data.append(team17.json())

    return Response({'connection': data})