from django.contrib import auth
from django.db import connection
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from LinkedSpace.views import loginView
from Posts.commentModel import Comments
from .serializers import *
import json
import uuid
import re
from django.urls import reverse
import requests
from permissions import CustomAuthentication, AccessPermission


from django.shortcuts import HttpResponse, render

from Posts.models import *
from .models import Author, FriendRequest, Inbox, Like, Followers

import django.core


from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.mixins import DestroyModelMixin

from .models import Author

from django.core.paginator import Paginator

# Create your views here.
def authorHome(request):
    template_name = 'LinkedSpace/Author/author.html'
    return render(request, template_name)

def clearInbox(request):
    if(request.user.is_authenticated):
        inbox = Inbox.objects.get(auth_pk = request.user)
        inbox.iPosts.set([], clear = True)
        inbox.iLikes.set([], clear = True)
        inbox.iFollows.set([], clear = True)

    return HttpResponseRedirect(reverse('author-inbox-frontend'))

def acceptFollow(request):
    # Code to accept follow request goes here.

    if(request.user.is_authenticated and request.user.id == request.POST["objectID"]):
        # Delete the friend request
        try:
            frequest = FriendRequest.objects.filter(actor = Author.objects.get(id=request.POST["actorID"]) , object = Author.objects.get(id=request.POST["objectID"]))
            frequest.delete()
        except:
            pass

        # Add to followers

        actor = Author.objects.get(id=request.POST["actorID"])
        object = Author.objects.get(id=request.POST["objectID"])

        ###### REDUNDANT #################
        followersObj = Followers.objects.get(pk = object.pk)

        if actor not in followersObj.items.all() and actor != object:
            followersObj.items.add(actor)
        ####################################

        followersAct = Followers.objects.get(pk = actor.pk)

        if object not in followersAct.items.all() and actor != object:
            followersAct.items.add(object)
        

        return HttpResponseRedirect(reverse('author-inbox-frontend'))

    else:
        return HttpResponseRedirect(reverse('login'))

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

    # Like Stuff
    # Calculte Number of Likes for Posts
    likeObjects = Like.objects.all()  
    allLikes = LikeSerializer(likeObjects,  many=True)   
    for post in posts:
        post["userLike"] = False
        post["numLikes"] = 0
        for like in allLikes.data:
            if post["id"] == like["object"]:
                post["numLikes"] += 1
    
    # Check which posts the user has already liked
    if(request.user.is_authenticated):
        likeObjects = Like.objects.filter(auth_pk = author)  
        userLikes = LikeSerializer(likeObjects,  many=True) 
        for post in posts:
            for like in userLikes.data:
                if post["id"] == like["object"]:
                    post["userLike"] = True


    context = {'user':author, 'posts':posts, 'likes':likes, 'follows': follows}

    template_name = 'LinkedSpace/Author/inbox.html'
    return HttpResponse(render(request, template_name, context),status=200)


@api_view(['GET',])
@authentication_classes([CustomAuthentication])
@permission_classes([AccessPermission])
def AuthorLikedView(request, auth_pk):
    author = Author.objects.get(pk = auth_pk)
    likeObjs = Like.objects.filter(auth_pk = author)

    Likes = LikeSerializer(likeObjs, read_only=True, many=True)
    likes = []

    for l in Likes.data:
        like = {}

        try:
            if("comment" not in l["object"]):
                # Public Post
                post = Post.objects.get(id = l["object"])
                if(post.visibility != 'PUBLIC'):
                    continue
            else:
                comment = Comments.objects.get(id = l["object"])
                post = comment.Post_pk
                if(post.visibility != 'PUBLIC'):
                    continue
                
        except Post.DoesNotExist:
            toDeleteLikes = Like.objects.filter(object = l["object"])
            toDeleteLikes.delete()
            continue
        
        for key in l:
            if(key != "context"):
                like[key] = l[key]
        like["@context"] = l["context"]
        like["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=l["author"]), fields=('type', 'id', 'displayName', 'host', 'url', 'github',)))[0]['fields']
        likes.append(like)

    response_dict = {
        "type": "liked",
        "items": likes
    }

    return Response(response_dict)

@api_view(['GET',])
@authentication_classes([CustomAuthentication])
@permission_classes([AccessPermission])
def AuthorsListView(request):

    authors = Author.objects.all()

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
def AuthorDetailView(request, auth_pk):
    try:
        author = Author.objects.get(pk=auth_pk)
    except Author.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        # serializer = AuthorSerializer(author, many=False)
        # return Response(serializer.data)
        
        template_name = 'LinkedSpace/authordetail.html'

        if request.user.is_authenticated:
            context = {'actor':request.user, 'object': author}

        else:
            context = {'object': author}

        return HttpResponse(render(request, template_name, context),status=200)

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
@authentication_classes([CustomAuthentication])
@permission_classes([AccessPermission])
def AuthorInboxView(request, auth_pk):
    try:
        author = Author.objects.get(pk=auth_pk)
        inbox =  Inbox.objects.get(pk=auth_pk)

    except Author.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


    ############ CONNECTION STUFF ###############

    foreign_authors_db_obj = Author.objects.filter(url__icontains = "social-dis") | Author.objects.filter(url__icontains = "unhindled") | Author.objects.filter(url__icontains = "cmput404f21t17") 

    fa_list = GetForeignAuthors()
    foreign_authors1 = fa_list[0]['items']
    foreign_authors2 = fa_list[1]['items']
    foreign_authors3 = fa_list[2]['items']

    foreign_authors = foreign_authors1 + foreign_authors2 + foreign_authors3

    for fadb in foreign_authors_db_obj:
        remove = True
        for fa in foreign_authors:
            if(fadb.url == fa["url"] or fa['url'].find("linkedspace-staging") != -1 or fa['url'].find("127.0.0.1:8000") != -1):
                foreign_authors.remove(fa)
                remove = False

        if(remove):
            fadb.delete()

    newIDs = []
    
    for fa in foreign_authors:
        fa["id"] = fa["url"]

        if fa["id"] in newIDs:
            continue

        newIDs.append(fa["id"])
        
        new_author = AuthorSerializer(data = fa)

        if new_author.is_valid():
            new_author.validated_data["id"] = fa["id"]
            new_author.validated_data["url"] = fa["url"]
            new_author.validated_data["email"] = fa["id"]
            new_author.validated_data["auth_pk"] = fa["id"]
            
            new_author.save()

        else:
            print(new_author.errors)
    
    ##############################################

    if request.method == "GET":
        serializer = InboxSerializer(inbox, many=False)
        data = getInboxData(serializer)

        page_number = request.GET.get('page')
        if 'size' in request.GET:
            page_size = request.GET.get('size')
        else:
            page_size = 5

        paginator = Paginator(data["items"], page_size)
        page_obj = paginator.get_page(page_number)

        data["items"] = page_obj.object_list


        return Response(data)

    if request.method == "DELETE":
        inbox.iPosts.set([], clear = True)
        inbox.iLikes.set([], clear = True)
        inbox.iFollows.set([], clear = True)
        
        serializer = InboxSerializer(inbox, many=False)
        data = getInboxData(serializer)
        return Response(data)

    if request.method == "POST":
        if(request.data["type"].lower() == "post"):
            serializerPost = PostSerializer(data=request.data)
            
            if serializerPost.is_valid():
                if(not "id" in request.data):

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
                    
                    post = Post.objects.filter(id= request.data["id"])
                        
                    if(post.count() == 0):
                        serializerPost.validated_data["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=request.data["author"]["id"]), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
                        serializerPost.validated_data["author_id"] = Author.objects.get(id=request.data["author"]["id"])
                        r_uid = uuid.uuid4().hex
                        uid = re.sub('-', '', r_uid)
                        serializerPost.validated_data["post_pk"] = request.data["id"].split("/")[-1]
                        serializerPost.validated_data["id"] = request.data["id"]

                        serializerPost.save()
                        post = Post.objects.get(id= request.data["id"])

                    inbox.iPosts.add(post)

                

                serializer = InboxSerializer(inbox, many=False)
                data = getInboxData(serializer)

                return Response(data)

            return Response(serializerPost.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if(request.data["type"].lower() == "like"):
            request.data["author"] = request.data["author"]["id"]
            request.data["context"] = request.data["@context"]
            serializerLike = LikeSerializer(data=request.data)

            if serializerLike.is_valid():
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

        
        if(request.data["type"].lower() == "follow"):
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


def GetForeignAuthors():
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

    return data


def GetForeignPosts():
    data = []

    team3 = requests.get('https://social-dis.herokuapp.com/posts', auth=('socialdistribution_t03','c404t03'))
    if team3.status_code == 200:
        data.append(team3.json())

    team15 = requests.get('https://unhindled.herokuapp.com/service/allposts/', auth=('connectionsuperuser','404connection'))
    if team15.status_code == 200:
        data.append(team15.json())

    team17 = requests.get('https://cmput404f21t17.herokuapp.com/service/connect/public/', auth=('4cbe2def-feaa-4bb7-bce5-09490ebfd71a','123456'))
    if team17.status_code == 200:
        data.append(team17.json())

    return data

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