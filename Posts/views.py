from django.conf import settings
from django.core import serializers
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect, render

from Posts.commentModel import Comments
from .serializers import PostSerializer
from Author.serializers import AuthorSerializer, LikeSerializer
from Author.models import Inbox, Like
from .models import Post, Author
from .form import PostForm
import json
import uuid
import re
import uuid
import re
import base64
from django.core.paginator import Paginator
import requests

# Create your views here.

def PostDetailView(request, post_pk, auth_pk = None):

    user = None
    if(request.user.is_authenticated):
        user = request.user

    postObj = Post.objects.get(pk = post_pk)
    postSeririaliezed = PostSerializer(postObj, many=False)
    post = postSeririaliezed.data


    # TODO Add logic to check for friend
    if(postObj.visibility.lower() == "public" or user == postObj.author_id):
    
        # If Content is image
        
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata
        
        post["categories"] = ' '.join(post["categories"]) # to format categories list for displaying correctly


        # Like Stuff
        # Calculte Number of Likes for Posts
        likeObjects = Like.objects.all()  
        likes = LikeSerializer(likeObjects,  many=True)   
        post["userLike"] = False
        post["numLikes"] = 0
        for like in likes.data:
            if post["id"] == like["object"]:
                post["numLikes"] += 1
        
        # Check which posts the user has already liked
        if(request.user.is_authenticated):
            likeObjects = Like.objects.filter(auth_pk = request.user)  
            userLikes = LikeSerializer(likeObjects,  many=True) 
            for like in userLikes.data:
                if post["id"] == like["object"]:
                    post["userLike"] = True


        context = {'post':post, 'user':user, 'post_pk':post_pk}

        template_name = 'LinkedSpace/Posts/post_detail.html'
        return HttpResponse(render(request, template_name, context),status=200)
    
    else:
        return HttpResponse(status=401)

def PostShare(request, post_pk, auth_pk=None):
    if request.method == 'POST':
        post = Post.objects.get(post_pk=post_pk)
        form = PostForm(request.POST, request.FILES)
        if form.is_valid() and request.user.id != post.author['id']:
            title = form.cleaned_data['title']
            descirption = form.cleaned_data['description'] + " (Shared from " + post.author['displayName'] + ")"
            categories = form.cleaned_data['categories']
            visibility = form.cleaned_data['visibility']
            unlisted = form.cleaned_data['unlisted']
            contentType = form.cleaned_data['contentType']

            if contentType == "application/app": 
                content = request.FILES['file'].read() #Inputfile
            elif contentType in ["image/png", "image/jpeg",]:
                content = base64.b64encode(request.FILES['file'].read()) #Inputfile
            else:
                content = form.cleaned_data["text"]

            source = settings.SERVER_URL + "/"
            origin = settings.SERVER_URL + "/"

            author_id = request.user
            id = request.user.id
            author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'displayName', 'url', 'github',)))[0]['fields']

            r_uid = uuid.uuid4().hex
            uid = re.sub('-', '', r_uid)
            id = id + '/posts/' + uid + "/"
            comments_id = id + "comments/"

            published = timezone.now()

            posts = Post(pk=uid, id=id, author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, contentType=contentType, count=0, size=10, categories=categories.split(' '),visibility=visibility, unlisted=unlisted, published=published, content=content, comments=comments_id)
            posts.save()

            return redirect(ManagePostsList)
        else:
            print(form.errors)
            print(form.data)
            form = PostForm()
            post = Post.objects.get(post_pk=post_pk)
            if request.user.id == post.author['id']:
                context = {'form': form, 'user':request.user, 'add': True, 'post': post}
                return render(request, "LinkedSpace/Posts/add_post.html", context)
            else:
                return redirect(ManagePostsList)
    else:
        form = PostForm()
        post = Post.objects.get(post_pk=post_pk)
        if request.user.id != post.author['id']:
            categories_as_string = ' '.join(post.categories)
            context = {'form': form, 'user':request.user, 'add': True, 'post': post, "stringified_categories": categories_as_string}
            return render(request, "LinkedSpace/Posts/add_post.html", context)
        else:
            return redirect(ManagePostsList)

def sendPOSTrequest(url, data):
    auth = getAuth(url)
    headers = {'content-type': 'application/json'}

    # preprocess url
    url = url +"/"
    url = url.replace("//", "/")
    url = url.replace("http", "https")
    url = url.replace("ss:", "s:")
    url = url.replace(":/", "://")

    print("data: ", data)
    print("url", url)

    x = requests.post(url, data = json.dumps(data), auth = auth, headers=headers)

    if x.status_code - 300 >= 0:
        url = url[:-1]
        x = requests.post(url, data = json.dumps(data), auth = auth, headers=headers)

        if x.status_code - 300 >= 0:
            url = url.replace(".com/", ".com/service/")
            x = requests.post(url, data = json.dumps(data), auth = auth, headers=headers)
    
    print("response", x.json())

    return x

def sendGETrequest(url):
    auth = getAuth(url)

    # preprocess url
    url = url +"/"
    url = url.replace("//", "/")
    url = url.replace("http", "https")
    url = url.replace("ss:", "s:")
    url = url.replace(":/", "://")

    x = requests.get(url, auth = auth)
    if x.status_code - 300 >= 0:
        url = url[:-1]
        x = requests.get(url, auth = auth)

        if x.status_code - 300 >= 0:
            url = url.replace(".com/", ".com/service/")
            x = requests.get(url, auth = auth)

    print(x.json())
    return x.status_code, x.json()

def getAuth(url):
    if "social-dis" in url:
        auth=('socialdistribution_t03','c404t03')
    elif "unhindled" in url:
        auth=('connectionsuperuser','404connection')
    elif "cmput404f21t17" in url:
        auth=('4cbe2def-feaa-4bb7-bce5-09490ebfd71a','123456')
    else:
        auth=('socialdistribution_t14','c404t14')
    
    return auth

def newLike(request, auth_pk = None, post_pk = None):
    # View to create a new like object after clicking the like button
    if request.user.is_authenticated:
        # TODO what is context supposed to be?
        context = request.POST["postID"] # "https://www.w3.org/ns/activitystreams"
        author = request.user
        object = request.POST["postID"]
        objectType = "post"

        if "comment" in object:
            objectType = "comment"
            post = Comments.objects.get(id = object)
            postAuthor = Author.objects.get(pk = post.auth_pk_str)
        else:
            post = Post.objects.get(id = object)
            postAuthor = Author.objects.get(email = post.author_id)
    
        summary = request.user.displayName + " liked " + postAuthor.displayName + "'s " + objectType
        
        if(Inbox.objects.filter(auth_pk = postAuthor).count() != 0):
            if(Like.objects.filter(auth_pk = author, object = object).count() == 0):
                like = Like(context = context, auth_pk = author, object = object, summary = summary)
                like.save()

                # Send to inbox
                if author != postAuthor:
                    inbox = Inbox.objects.get(auth_pk = postAuthor)
                    inbox.iLikes.add(like)
            else:
                like = Like.objects.filter(auth_pk = author, object = object)
                like.delete()

        else:
            # Send like to foreign author's inbox
            # TODO TEAM 17
            url = postAuthor.url + "/inbox/"
            authorSerialized = AuthorSerializer(request.user, many = False)
            data = {
            "type": "like",
            "@context": context,
            "object": object,
            "summary": summary,
            "author": authorSerialized.data
            }

            sendPOSTrequest(url, data)

        if(request.POST["context"] == "stream"):
            return HttpResponseRedirect(reverse('user-stream-view', kwargs={ 'auth_pk': auth_pk }))
        elif(request.POST["context"] == "comments"):
            return HttpResponseRedirect(reverse('comment-list', kwargs={ 'post_pk': post_pk }))
        elif(request.POST["context"] == "post-detail"):
            return HttpResponseRedirect(reverse('post-detail-view', kwargs={ 'post_pk': post_pk }))
        else:
            return HttpResponseRedirect(reverse('author-inbox-frontend'))

    else:
        return HttpResponseRedirect(reverse('login'))

def processLikes(request, posts):
    # Like Stuff
    # Calculte Number of Likes for Posts
    # TODO TEAM 17
    
    likeObjects = Like.objects.all()  
    likes_local = LikeSerializer(likeObjects,  many=True)   
    for post in posts:
        if "linkedspace" in post["id"]:
            post["userLike"] = False
            post["numLikes"] = 0
            for like in likes_local.data:
                if post["id"] == like["object"] or post["origin"] == like["object"]:
                    post["numLikes"] += 1

        else:

            post["userLike"] = False
            post["numLikes"] = 0

            code, likes = sendGETrequest(post["id"] + "/likes/")

            if code - 300 < 0:
                if("items" in likes):
                    post["numLikes"] = len(likes["items"])
                else:
                    post["numLikes"] = len(likes)
    
    # Check which posts the user has already liked
    if(request.user.is_authenticated):
        likeObjects = Like.objects.filter(auth_pk = request.user)  
        userLikes = LikeSerializer(likeObjects,  many=True) 
        for post in posts:
            if "linkedspace" in post["id"]:
                for like in userLikes.data:
                    if post["id"] == like["object"] or post["origin"] == like["object"]:
                        post["userLike"] = True
            else:
                
                code, likes = sendGETrequest(post["id"] + "/likes/")

                if code - 300 < 0:
                    if "items" in likes:
                        for like in likes["items"]:
                            if post["id"] == like["object"]:
                                post["userLike"] = True
                    else:
                        for like in likes:
                            if post["id"] == like["object"]:
                                post["userLike"] = True
                

    return posts

# TODO Better CSS for Stream
# Non API view, Displays the users posts and github activity
def UserStreamView(request, auth_pk):
    # TODO Add Github API stuff here
    
    if(request.user.is_authenticated and request.user.pk == auth_pk):
        author = request.user
        postsObjects = Post.objects.filter(author_id=author.pk) # | Post.objects.filter(visibility = "PUBLIC")

    else:
        # TODO Friend Posts in stream
        author = Author.objects.get(pk = auth_pk)
        postsObjects = Post.objects.filter(author_id=author.pk, visibility = "Public") | Post.objects.filter(author_id=author.pk, visibility = "PUBLIC")
    
    postsObjects = postsObjects.order_by('-published')

    posts = PostSerializer(postsObjects, many=True)
    
    # If Content is image
    for post in posts.data:
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata
        post["categories"] = ' '.join(post["categories"]) # to format categories list for displaying correctly
    
    posts = processLikes(request, posts.data)

    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 5

    paginator = Paginator(posts, page_size)
    page_obj = paginator.get_page(page_number)

    context = {'posts':page_obj, 'user':author}

    template_name = 'LinkedSpace/Posts/posts.html'
    return HttpResponse(render(request, template_name, context),status=200)

def newPost(request, auth_pk=None):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        title = form.cleaned_data['title']
        descirption = form.cleaned_data['description']
        categories = form.cleaned_data['categories']
        visibility = form.cleaned_data['visibility']
        unlisted = form.cleaned_data['unlisted']
        contentType = form.cleaned_data['contentType']

        if contentType == "application/app": 
            content = request.FILES['file'].read() #Inputfile
        elif contentType in ["image/png", "image/jpeg",]:
            content = base64.b64encode(request.FILES['file'].read()) #Inputfile
        else:
            content = form.cleaned_data["text"]

        source = settings.SERVER_URL + "/"
        origin = settings.SERVER_URL + "/"

        author_id = request.user
        id = request.user.id
        author = json.loads(serializers.serialize('json', Author.objects.filter(id=request.user.id), fields=('type', 'id', 'host', 'displayName', 'url', 'github',)))[0]['fields']

        r_uid = uuid.uuid4().hex
        uid = re.sub('-', '', r_uid)
        id = id + '/posts/' + uid + "/"
        comments_id = id + "comments/"

        published = timezone.now()

        posts = Post(pk=uid, id=id, author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, contentType=contentType, count=0, size=10, categories=categories.split(' '),visibility=visibility, unlisted=unlisted, published=published, content=content, comments=comments_id)
        posts.save()

        return redirect(ManagePostsList)
    else:
        # print(form.errors)
        # print(form.data)
        form = PostForm()
        context = {'form': form, 'user':request.user, 'add': True}
        return render(request, "LinkedSpace/Posts/add_post.html", context)

def ManagePostsList(request, auth_pk=None):
    posts = list(Post.objects.filter(author_id=request.user).order_by('-published'))
    
    # If Content is image
    for post in posts:
        post.isImage = False
        if(post.contentType == "image/png" or post.contentType == "image/jpeg"):
            post.isImage = True
            imgdata = post.content[2:-1]
            post.image = imgdata
        post.categories = ' '.join(post.categories) # to format categories list for displaying correctly
    
    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 5

    paginator = Paginator(posts, page_size)
    page_obj = paginator.get_page(page_number)

    return render(request, "LinkedSpace/Posts/manage_posts.html", {'posts': page_obj})

def delete_Post(request, post_pk, auth_pk=None):
    post = Post.objects.get(post_pk=post_pk)
    if request.user.id == post.author['id']:
        post.delete()
    return redirect(ManagePostsList)

def edit_Post(request, post_pk, auth_pk=None):
    if request.method == 'POST':
        post = Post.objects.get(post_pk=post_pk)
        form = PostForm(request.POST, request.FILES)
        if form.is_valid() and request.user.id == post.author['id']:
            title = form.cleaned_data['title']
            descirption = form.cleaned_data['description']
            categories = form.cleaned_data['categories']
            visibility = form.cleaned_data['visibility']
            unlisted = form.cleaned_data['unlisted']
            contentType = form.cleaned_data['contentType']

            if contentType == "application/app": 
                content = request.FILES['file'].read() #Inputfile
            elif contentType in ["image/png", "image/jpeg",]:
                content = base64.b64encode(request.FILES['file'].read()) #Inputfile
            else:
                content = form.cleaned_data["text"]

            post.title = title
            post.description = descirption
            post.categories = categories.split(' ')
            post.visibility = visibility
            post.unlisted = unlisted
            post.contentType = contentType
            post.content = content
            post.save()

            return redirect(ManagePostsList)
        else:
            print(form.errors)
            print(form.data)
            form = PostForm()
            post = Post.objects.get(post_pk=post_pk)
            if request.user.id == post.author['id']:
                context = {'form': form, 'user':request.user, 'add': False, 'post': post}
                return render(request, "LinkedSpace/Posts/add_post.html", context)
            else:
                return redirect(ManagePostsList)
    else:
        form = PostForm()
        post = Post.objects.get(post_pk=post_pk)
        if request.user.id == post.author['id']:
            categories_as_string = ' '.join(post.categories)
            context = {'form': form, 'user':request.user, 'add': False, 'post': post, "stringified_categories": categories_as_string}
            return render(request, "LinkedSpace/Posts/add_post.html", context)
        else:
            return redirect(ManagePostsList)
        # form = PostForm()
        # post = Post.objects.get(post_pk=post_pk)
        # if request.user.id == post.author['id']:
        #     context = {'form': form, 'user':request.user, 'add': False, 'post': post}
        #     return render(request, "LinkedSpace/Posts/add_post.html", context)
        # else:
        #     return redirect(ManagePostsList)
