from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from LinkedSpace.views import loginView
from .serializers import *
import json
import uuid
import re
from django.urls import reverse


from django.shortcuts import HttpResponse, render

from Posts.models import *
from .models import Author, Inbox, Like

import django.core


from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.mixins import DestroyModelMixin

from .models import Author

def getInboxData(serializer):
        iPosts = serializer.data.pop("iPosts")
        iLikes = serializer.data.pop("iLikes")

        data = {}
        likes = []
        for key in serializer.data:
            if(key != "iPosts" and key != "iLikes"):
                data[key] = serializer.data[key]

        for l in iLikes:
            like = {}
            for key in l:
                if(key != "context"):
                    like[key] = l[key]
            like["@context"] = l["context"]
            like["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=l["author"]), fields=('type', 'id', 'displayName', 'host', 'url', 'github',)))[0]['fields']
            likes.append(like)

        
        for item in iPosts:
            data["items"].append(item)
        for item in likes:
            data["items"].append(item)
        
        return data


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


@api_view(['GET', 'POST', 'DELETE'])
def AuthorInboxView(request, auth_pk):
    try:
        author = Author.objects.get(pk=auth_pk)

        # if not the inbox of logged in user then redirect to login page
        # TODO is this what we want?
        if(request.user.id != author.id):
            return HttpResponseRedirect(reverse('login'))

        inbox =  Inbox.objects.get(pk=auth_pk)
    except Author.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = InboxSerializer(inbox, many=False)
        data = getInboxData(serializer)

        return Response(data)

    if request.method == "DELETE":
        inbox.iPosts.set([None])
        inbox.iLikes.set([None])
        
        serializer = InboxSerializer(inbox, many=False)
        data = getInboxData(serializer)
        return Response(data)

    if request.method == "POST":
        if(request.data["type"] == "post"):
            serializerPost = PostSerializer(data=request.data)
            
            if serializerPost.is_valid():
                serializerPost.validated_data["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
                serializerPost.validated_data["author_id"] = Author.objects.get(id=request.user.id)
                r_uid = uuid.uuid4().hex
                uid = re.sub('-', '', r_uid)
                serializerPost.validated_data["post_pk"] = uid
                serializerPost.validated_data["id"] = request.user.id + '/posts/' + uid

                serializerPost.save()

                post = Post.objects.get(pk= uid)
                inbox.iPosts.add(post)

                serializer = InboxSerializer(inbox, many=False)
                data = getInboxData(serializer)

                return Response(data)

            return Response(serializerPost.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if(request.data["type"] == "like"):
            request.data["author"] = request.data["author"]["id"]
            request.data["context"] = request.data["@context"]
            serializerLike = LikeSerializer(data=request.data)

            if serializerLike.is_valid():
                r_uid = uuid.uuid4().hex
                uid = re.sub('-', '', r_uid)
                serializerLike.validated_data["like_id"] = uid
                serializerLike.validated_data["auth_pk"] = Author.objects.get(id=request.data["author"])
                serializerLike.validated_data.pop("get_author")

                serializerLike.save()

                like = Like.objects.get(pk= uid)

                inbox.iLikes.add(like)
                
                serializer = InboxSerializer(inbox, many=False)
                data = getInboxData(serializer)
                return Response(data)
            
            return Response(serializerLike.errors, status=status.HTTP_400_BAD_REQUEST)

        if(request.data["type"] == "follow"):
            pass

# DEPRECATED INBOX VIEW
# class DeleteInboxMixin(DestroyModelMixin):
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         self.perform_destroy(instance)
#         return Response()

#     def perform_destroy(self, instance):
#         instance.items.set([None])

# class AuthorInboxView(DeleteInboxMixin ,generics.RetrieveDestroyAPIView):
#     serializer_class = InboxSerializer
#     queryset = Inbox.objects.all()
#     lookup_field = 'auth_pk'
#     http_method_names = ["get", "delete"]

