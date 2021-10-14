from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

from django.shortcuts import HttpResponse, render

from Posts.models import *
from .models import Author, Inbox


from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.mixins import DestroyModelMixin

from .models import Author
# Create your views here.
def authorHome(request):
    template_name = 'LinkedSpace/Author/author.html'
    return render(request, template_name)

@api_view(['GET',])
def AuthorsListView(request):

    authors = Author.objects.all()
    serializer = AuthorSerializer(authors, many=True)

    response_dict = {
        "type": "authors",
        "items": serializer.data
    }

    return Response(response_dict)

@api_view(['GET', 'POST',])
def AuthorDetailView(request, auth_pk):
	try:
		author = Author.objects.get(pk=auth_pk)
	except Author.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	if request.method == "GET":
		serializer = AuthorSerializer(author, many=False)
		return Response(serializer.data)

	if request.method == "POST":
		serializer = AuthorProfileSerializer(instance=author, data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['DELETE'])
# def AuthorDeleteView(request, pk):
# 	author = Author.objects.get(id=pk)
# 	author.delete()


# 	return Response('Item succesfully deleted.')

    # def get_object(self):
    #     id = self.kwargs['auth_pk']
    #     try:
    #         return get_object_or_404(Author.objects, id=id)
    #     except Exception as e:
    #         raise ValidationError({str(e): status.HTTP_404_NOT_FOUND})

class DeleteInboxMixin(DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response()

    def perform_destroy(self, instance):
        instance.items.set([None])

class AuthorInboxView(DeleteInboxMixin ,generics.RetrieveDestroyAPIView):
    serializer_class = InboxSerializer
    queryset = Inbox.objects.all()
    lookup_field = 'auth_pk'
    http_method_names = ["get", "delete"]

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

