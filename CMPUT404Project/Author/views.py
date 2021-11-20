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
import requests


from django.shortcuts import HttpResponse, render

from Posts.models import *
from .models import Author, FriendRequest, Inbox, Like, Followers

import django.core


from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.mixins import DestroyModelMixin

from .models import Author

# Create your views here.
def authorHome(request):
    template_name = 'LinkedSpace/Author/author.html'
    return render(request, template_name)

def clearInbox(request):
    if(request.user.is_authenticated):
        inbox = Inbox.objects.get(auth_pk = request.user)
        inbox.iPosts.set([None])
        inbox.iLikes.set([None])
        inbox.iFollows.set([None])

    return HttpResponseRedirect(reverse('author-inbox-frontend'))

def acceptFollow(request):
    # Code to accept follow request goes here.

    if(request.user.id == request.POST["objectID"]):
        # Delete the friend request
        try:
            frequest = FriendRequest.objects.filter(actor = Author.objects.get(id=request.POST["actorID"]) , object = Author.objects.get(id=request.POST["objectID"]))
            frequest.delete()
        except:
            pass

        # Add to followers

        actor = Author.objects.get(id=request.POST["actorID"])
        object = Author.objects.get(id=request.POST["objectID"])

        followersObj = Followers.objects.get(pk = object.pk)

        if actor not in followersObj.items.all():
            followersObj.items.add(actor)

        # Follow is not bidirectional
        # followersAct = Followers.objects.get(pk = actor.pk)

        # if object not in followersAct.items.all():
        #     followersAct.items.add(object)
        

    return HttpResponseRedirect(reverse('author-inbox-frontend'))

def MyInboxView(request):
    # Non API view, Displays the users posts and github activity
    # TODO Better CSS for front-end of inbox
    author = request.user
    inbox =  Inbox.objects.get(pk=author.pk)
    serializer = InboxSerializer(inbox, many=False)
    data = getInboxData(serializer)
    items = data["items"]

    posts = [i for i in items if i["type"] == "post"]
    posts.reverse()

    likes = [i for i in items if i["type"] == "like"]
    likes.reverse()

    follows = [i for i in items if i["type"] == "follow"]
    follows.reverse()
    

    
    # If Content is image
    for post in posts:
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata

    
    # # Determine if like is for post or comment
    # for like in likes:
    #     if "comment" in like["object"]:
    #         like["isComment"] = True
    #     else:
    #         like["isComment"] = False


    context = {'user':author, 'posts':posts, 'likes':likes, 'follows': follows}

    template_name = 'LinkedSpace/Author/inbox.html'
    return HttpResponse(render(request, template_name, context),status=200)

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


# Auxillary Function for Inbox
def getInboxData(serializer):
        iPosts = serializer.data.pop("iPosts")
        iLikes = serializer.data.pop("iLikes")
        iFollows = serializer.data.pop("iFollows")

        data = {}
        likes = []
        for key in serializer.data:
            if(key != "iPosts" and key != "iLikes" and key != "iFollows"):
                data[key] = serializer.data[key]

        for l in iLikes:
            like = {}
            for key in l:
                if(key != "context"):
                    like[key] = l[key]
            like["@context"] = l["context"]
            like["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=l["author"]), fields=('type', 'id', 'displayName', 'host', 'url', 'github',)))[0]['fields']
            likes.append(like)

        for f in iFollows:
            f["actor"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=f["actor"]), fields=('type', 'id', 'displayName', 'host', 'url', 'github',)))[0]['fields']
            f["object"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=f["object"]), fields=('type', 'id', 'displayName', 'host', 'url', 'github',)))[0]['fields']

        for item in iPosts:
            data["items"].append(item)
        for item in likes:
            data["items"].append(item)
        for item in iFollows:
            data["items"].append(item)
        
        return data


@api_view(['GET', 'POST', 'DELETE'])
def AuthorInboxView(request, auth_pk):
    try:
        author = Author.objects.get(pk=auth_pk)

        # if not the inbox of logged in user then redirect to login page
        # TODO is this what we want?
        # if(request.user.id != author.id or not request.user.is_authenticated):
        #     return HttpResponseRedirect(reverse('login'))

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
        inbox.iFollows.set([None])
        
        serializer = InboxSerializer(inbox, many=False)
        data = getInboxData(serializer)
        return Response(data)

    if request.method == "POST":
        if(request.data["type"] == "post"):
            serializerPost = PostSerializer(data=request.data)
            
            if serializerPost.is_valid():
                if(not "id" in serializerPost.validated_data):

                    serializerPost.validated_data["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
                    serializerPost.validated_data["author_id"] = Author.objects.get(id=request.user.id)
                    r_uid = uuid.uuid4().hex
                    uid = re.sub('-', '', r_uid)
                    serializerPost.validated_data["post_pk"] = uid
                    serializerPost.validated_data["id"] = request.user.id + '/posts/' + uid

                    serializerPost.save()
                    post = Post.objects.get(pk= uid)
                    inbox.iPosts.add(post)
                
                else:
                    post = Post.objects.get(id= serializerPost.validated_data["id"])
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
                # r_uid = uuid.uuid4().hex
                # uid = re.sub('-', '', r_uid)
                # serializerLike.validated_data["like_id"] = uid
                serializerLike.validated_data["auth_pk"] = Author.objects.get(id=request.data["author"])
                serializerLike.validated_data.pop("get_author")

                if(Like.objects.filter(auth_pk = Author.objects.get(id=request.data["author"]), object = request.data["object"]).count() == 0):
                    serializerLike.save()

                like = Like.objects.get(auth_pk = Author.objects.get(id=request.data["author"]), object = request.data["object"])

                inbox.iLikes.add(like)
                
                serializer = InboxSerializer(inbox, many=False)
                data = getInboxData(serializer)
                return Response(data)
            
            return Response(serializerLike.errors, status=status.HTTP_400_BAD_REQUEST)

        if(request.data["type"] == "follow"):
            request.data["actor"] = request.data["actor"]["id"]
            request.data["object"] = request.data["object"]["id"]
            serializerFollow = FriendRequestSerializer(data=request.data)

            if serializerFollow.is_valid():
                serializerFollow.validated_data["actor"] = Author.objects.get(id=request.data["actor"])
                serializerFollow.validated_data["object"] = Author.objects.get(id=request.data["object"])
                serializerFollow.validated_data.pop("get_actor")
                serializerFollow.validated_data.pop("get_object")
                
                if(FriendRequest.objects.filter(actor = Author.objects.get(id=request.data["actor"]) , object = Author.objects.get(id=request.data["object"])).count() == 0):
                    serializerFollow.save()

                follow = FriendRequest.objects.get(actor = Author.objects.get(id=request.data["actor"]) , object = Author.objects.get(id=request.data["object"]))

                inbox.iFollows.add(follow)

                serializer = InboxSerializer(inbox, many=False)
                data = getInboxData(serializer)
                return Response(data)
            
            return Response(serializerFollow.errors, status=status.HTTP_400_BAD_REQUEST)


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



