from django.contrib import auth
from django.db import connection
from django.http.response import HttpResponseRedirect, HttpResponseRedirectBase
from django.shortcuts import render
from CMPUT404Project import settings
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
from Posts.views import processLikes, sendGETrequest, sendPOSTrequest

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

        followersObj = Followers.objects.get(pk = object.pk)

        if actor not in followersObj.items.all() and actor != object:
            followersObj.items.add(actor)

        return HttpResponseRedirect(reverse('author-inbox-frontend'))

    else:
        return HttpResponseRedirect(reverse('login'))

def MyInboxView(request):
    # Non API view, Displays the users posts and github activity
    # TODO Better CSS for front-end of inbox
    updateForeignAuthors()
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
        post["localid"] = settings.SERVER_URL + "/author/" + str(request.user.pk) + "/posts/" + post["id"].split("/")[-1]
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata

    
    
    posts = processLikes(request, posts)


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
                if(post.visibility.lower() != "public"):
                    continue
            else:
                comment = Comments.objects.get(id = l["object"])
                post = comment.Post_pk
                if(post.visibility.lower() != "public"):
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
        git_username = author.github.replace("http://github.com/", "")

        if request.user.is_authenticated:

            context = {'actor':request.user, 'object': author, 'git_username':git_username}

        else:
            context = {'object': author, 'git_username':git_username}

        return HttpResponse(render(request, template_name, context),status=200)

    if request.method == "POST":
        serializer = AuthorProfileSerializer(instance=author, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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
            code, _ = sendGETrequest(item["id"])

            # Check if foreign post is deleted
            if code - 300 < 0 or "friend" in item["visibility"].lower():
                data["items"].append(item)
            else:
                # delete foreign post from db
                postToDelete = Post.objects.get(id = item["id"])
                postToDelete.delete()

        for item in likes:
            data["items"].append(item)
        for item in iFollows:
            data["items"].append(item)
        
        return data


def updateForeignAuthors():
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
            if(fadb.url == fa["url"] or fa['url'].find("linkedspace") != -1 or fa['url'].find("127.0.0.1:8000") != -1):
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
        
        if "github" not in fa or not fa["github"]:
            fa["github"] = "https://github.com/"
        new_author = AuthorSerializer(data = fa)

        if new_author.is_valid():
            new_author.validated_data["id"] = fa["id"]
            new_author.validated_data["url"] = fa["url"]
            new_author.validated_data["email"] = fa["id"]
            new_author.validated_data["auth_pk"] = fa["id"].split("/")[-1]
            
            new_author.save()

        else:
            print(new_author.errors)
    
    ##############################################

@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([CustomAuthentication])
@permission_classes([AccessPermission])
def AuthorInboxView(request, auth_pk):
    try:
        author = Author.objects.get(pk=auth_pk)
        inbox =  Inbox.objects.get(pk=auth_pk)

    except Author.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


    updateForeignAuthors()

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
            if "image" in request.data["contentType"]:
                request.data["contentType"] = "image/png"
                request.data["content"] =  "b'" + request.data["content"].split("base64,")[-1] + "'"

            request.data["source"] = "https://linkedspace-staging.herokuapp.com/posts/connection/"
            serializerPost = PostSerializer(data=request.data)
            
            if serializerPost.is_valid():
                if(not "id" in request.data):

                    serializerPost.validated_data["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
                    serializerPost.validated_data["author_id"] = Author.objects.get(id=request.user.id)

                    if "comments" in request.data:
                        serializerPost.validated_data["comments"] = request.data["comments"]

                    r_uid = uuid.uuid4().hex
                    uid = re.sub('-', '', r_uid)
                    serializerPost.validated_data["post_pk"] = uid
                    serializerPost.validated_data["id"] = request.user.id + '/posts/' + uid

                    serializerPost.save()
                    post = Post.objects.get(pk= uid)
                    inbox.iPosts.add(post)
                
                else:
                    
                    postSet = Post.objects.filter(id= request.data["id"])
                        
                    if(postSet.count() == 0):
                        serializerPost.validated_data["author"] = json.loads(django.core.serializers.serialize('json', Author.objects.filter(id=request.data["author"]["id"]), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']
                        serializerPost.validated_data["author_id"] = Author.objects.get(id=request.data["author"]["id"])
                        
                        if "comments" in request.data:
                            serializerPost.validated_data["comments"] = request.data["comments"]
                        
                        r_uid = uuid.uuid4().hex
                        uid = re.sub('-', '', r_uid)
                        serializerPost.validated_data["post_pk"] = request.data["id"].split("/")[-1]
                        serializerPost.validated_data["id"] = request.data["id"]

                        serializerPost.save()
                        post = Post.objects.get(id= request.data["id"])

                    else:
                      post =  Post.objects.get(id= request.data["id"])
                    inbox.iPosts.add(post)

                

                serializer = InboxSerializer(inbox, many=False)
                data = getInboxData(serializer)

                return Response(data)

            return Response(serializerPost.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if(request.data["type"].lower() == "like"):
            actor_name = request.data["author"]["displayName"]
            request.data["author"] = request.data["author"]["id"]
            request.data["context"] = request.data["@context"]
            objectType = "post"
            if("summary" not in request.data):
                if "comment" in request.data["object"]:
                    objectType = "comment"
                    post = Comments.objects.get(id = request.data["object"])
                    postAuthor = Author.objects.get(pk = post.auth_pk_str)
                else:
                    post = Post.objects.get(id = request.data["object"])
                    postAuthor = Author.objects.get(email = post.author_id)
            
                request.data['summary'] = actor_name + " liked " + postAuthor.displayName + "'s " + objectType
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
@api_view(['POST',])
def AuthorInboxViewFrontend(request, auth_pk):
    if request.method == 'POST':

        if request.user.is_authenticated:


            actor = Author.objects.get(id = request.POST["actor"])
            objectauthor = Author.objects.get(id = request.POST["object"])

            summary = actor.displayName + ' wants to follow ' + objectauthor.displayName

            type = request.POST["type"]

            inbox =  Inbox.objects.get(pk=auth_pk)
            inbox.iFollows.add(FriendRequest.objects.create(summary=summary, type = type, actor = actor, object = objectauthor))
            
            followersObj = Followers.objects.get(pk = objectauthor.pk)

            if actor not in followersObj.items.all() and actor != objectauthor:
                followersObj.items.add(actor)
            
            return HttpResponseRedirect('/authors')

def GetForeignAuthors():
    data = []

    team3 = requests.get('https://social-dis.herokuapp.com/authors?size=1000', auth=('socialdistribution_t03','c404t03'))
    if team3.status_code == 200:
        data.append(team3.json())

    team15 = requests.get('https://unhindled.herokuapp.com/service/authors/?size=1000', auth=('connectionsuperuser','404connection'))
    if team15.status_code == 200:
        data.append(team15.json())

    team17 = requests.get('https://cmput404f21t17.herokuapp.com/service/connect/public/author/?size=1000', auth=('4cbe2def-feaa-4bb7-bce5-09490ebfd71a','123456'))
    if team17.status_code == 200:
        data.append(team17.json())

    return data


def GetForeignPosts():
    data = []

    team3 = requests.get('https://social-dis.herokuapp.com/posts?size=1000', auth=('socialdistribution_t03','c404t03'))
    if team3.status_code == 200:
        data.append(team3.json())

    team15 = requests.get('https://unhindled.herokuapp.com/service/allposts/?size=1000', auth=('connectionsuperuser','404connection'))
    if team15.status_code == 200:
        data.append(team15.json())

    team17 = requests.get('https://cmput404f21t17.herokuapp.com/service/connect/public/?size=1000', auth=('4cbe2def-feaa-4bb7-bce5-09490ebfd71a','123456'))
    if team17.status_code == 200:
        data.append(team17.json())

    return data

@api_view(['GET',])
def AuthorsConnection(request, auth_id=None):
    data = []

    team3 = requests.get('https://social-dis.herokuapp.com/authors?size=1000', auth=('socialdistribution_t03','c404t03'))
    if team3.status_code == 200:
        data.append(team3.json())

    team15 = requests.get('https://unhindled.herokuapp.com/service/authors/?size=1000', auth=('connectionsuperuser','404connection'))
    if team15.status_code == 200:
        data.append(team15.json())

    team17 = requests.get('https://cmput404f21t17.herokuapp.com/service/connect/public/author/?size=1000', auth=('4cbe2def-feaa-4bb7-bce5-09490ebfd71a','123456'))
    if team17.status_code == 200:
        data.append(team17.json())

    return Response({'connection': data})

@api_view(['GET',])
def ForeignAuthorsFrontend(request):
    if request.method == 'GET':
        authorList = GetForeignAuthors()

        context = {'Foreigners':authorList}

        return HttpResponse(render(template_name='LinkedSpace/foreignauthors.html', request=request, context= context), status = 200)
        

    

