from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

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