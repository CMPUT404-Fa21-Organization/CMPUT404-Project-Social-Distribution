from django.shortcuts import HttpResponse, render

from .serializers import *
from Posts.models import *
from .models import Author, Inbox


from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
def authorHome(request):
    template_name = 'LinkedSpace/Author/author.html'
    return render(request, template_name)

# ========== These views are deprecated, remains in code temporarily until urls can be resolved =============
@api_view(['GET'])
def authorsList(request):

    authors = Author.objects.all()
    serializer = AuthorSerializer(authors, many=True)

    response_dict = {
        "type": "authors",
        "items": serializer.data
    }

    return Response(response_dict)

@api_view(['PUT'])
def authorCreate(request):

    serializer = AuthorSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)
# ==========================================================================================================

# GET all Authors
class AuthorListView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    http_method_names = ['get']
    serializer_class = AuthorSerializer

# POST/PUT Author
class AuthorCreateView(generics.CreateAPIView):
    serializer_class = AuthorRegisterSerializer
    # http_method_names = ['POST', 'PUT']

# https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
class AuthorLoginView(generics.GenericAPIView):
    serializer_class = AuthorLoginSerializer

    # request.user will be a Django User instance
    # request.auth will be a rest_framework.authtoken.models.Token instance
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        author = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=author)
        return Response({
            'token': token.key,
            # don't think it's necessary to return anything other then the token upon authentication ...
            # 'user_id': author.pk,
            # 'email': author.email
        })

class AuthorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = AuthorProfileSerializer
    authenticate_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Author.objects.all()
    lookup_field = 'auth_pk'
    http_method_names = ["get", "put"]

    # def get_object(self):
    #     id = self.kwargs['pk']
    #     try:
    #         return get_object_or_404(Author.objects, id=id)
    #     except Exception as e:
    #         raise ValidationError({str(e): status.HTTP_404_NOT_FOUND})

# https://codefellows.github.io/sea-python-401d5/lectures/django_cbv2.html#the-get-object-method
class AuthorDetailView(generics.RetrieveAPIView):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    lookup_field = 'auth_pk'
    # authenticate_classes = (authentication.TokenAuthentication,)
    # permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get"]

    # def get_object(self):
    #     id = self.kwargs['auth_pk']
    #     try:
    #         return get_object_or_404(Author.objects, id=id)
    #     except Exception as e:
    #         raise ValidationError({str(e): status.HTTP_404_NOT_FOUND})


class AuthorInboxView(generics.RetrieveAPIView):
    serializer_class = InboxSerializer
    queryset = Inbox.objects.all()
    lookup_field = 'author'
    # authenticate_classes = (authentication.TokenAuthentication,)
    # permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get"]

# @api_view(['GET'])
# def authorInbox(request, id):
#     author = Inbox.objects.get(author=id)
#     serializer = InboxSerializer(author, many=False)

#     return Response(serializer.data)

# @api_view(['POST'])
# def authorInboxUpdate(request, id):

#     author = Inbox.objects.get(author=id)
#     serializer = InboxSerializer(instance=author, data=request.data)

#     if serializer.is_valid():
#         serializer.save()

#     return Response(serializer.data)

