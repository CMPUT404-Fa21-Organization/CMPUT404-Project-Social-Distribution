import django
from django.conf import settings
from django.core import serializers
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect, render
from requests.models import MissingSchema

from Posts.commentModel import Comments
from .serializers import PostSerializer
from Author.serializers import AuthorSerializer, LikeSerializer
from Author.models import Inbox, Like, Followers
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

def PostDetailView(request, post_pk, auth_pk = None):

    user = None
    if(request.user.is_authenticated):
        user = request.user
    postObj = Post.objects.get(pk = post_pk)
    postSeririaliezed = PostSerializer(postObj, many=False)
    post = postSeririaliezed.data


    # TODO Add logic to check for friend
    if(postObj.visibility.lower() == "public" or user == postObj.author_id):
    
        # resolve team 03 image formatting
        if 'social-dis' in post["id"]:
            if 'image' in post['contentType']:
                post["isImage"] = True
                index = post['content'].index('base64,')
                imgdata = post["content"][index+7:]
                post["image"] = imgdata

        # resolve team 15 image formatting
        if 'undhindled' in post["id"]:
            if 'image' in post['contentType']:
                post["isImage"] = True
                index = post['content'].index('base64,')
                imgdata = post["content"][index+7:]
                post["image"] = imgdata

        # resolve team 17 image formatting
        if 'cmput404f21t17' in post["origin"]:
            if 'image' in post['contentType']:
                post["isImage"] = True
                index = post['content'].index('base64,')
                imgdata = post["content"][index+7:]
                post["image"] = imgdata

        if 'linkedspace-staging' in post["id"]:
            # If Content is image
            post["isImage"] = False
            if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
                post["isImage"] = True
                imgdata = post["content"][2:-1]
                post["image"] = imgdata

        post["categories"] = ' '.join(post["categories"]) # to format categories list for displaying correctly

        post = processLikes(request, [post])[0]


        context = {'post':post, 'user':user, 'post_pk':post_pk}

        template_name = 'LinkedSpace/Posts/post_detail.html'
        return HttpResponse(render(request, template_name, context),status=200)
    
    else:
        return HttpResponse(status=401)

def PostShare(request, post_pk, auth_pk=None):
    og_post = Post.objects.get(post_pk=post_pk)
    title = og_post.title
    description = og_post.description + " (Shared from " + og_post.author['displayName'] + ")"
    categories = og_post.categories
    visibility = og_post.visibility
    unlisted = og_post.unlisted
    contentType = og_post.contentType
    content = og_post.content

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

    new_post = Post(pk=uid, id=id, author_id=author_id, author=author, title=title, source=source, origin=origin, description=description, contentType=contentType, count=0, size=10, categories=categories, visibility=visibility, unlisted=unlisted, published=published, content=content, comments=comments_id)
    new_post.save()

    return redirect(ManagePostsList)

def sendPOSTrequest(url, data):
    auth = getAuth(url)
    headers = {'content-type': 'application/json'}

    # preprocess url
    url = url +"/"
    url = url.replace("//", "/")
    url = url.replace("http", "https")
    url = url.replace("httpss", "https")
    url = url.replace("ss:", "s:")
    url = url.replace(":/", "://")

    # print("data: ", data)
    # print("url", url)

    x = requests.post(url, data = json.dumps(data), auth = auth, headers=headers)

    if x.status_code - 300 >= 0:
        url = url[:-1]
        x = requests.post(url, data = json.dumps(data), auth = auth, headers=headers)

        if x.status_code - 300 >= 0:
            url = url.replace(".com/", ".com/service/")
            x = requests.post(url, data = json.dumps(data), auth = auth, headers=headers)

            if x.status_code - 300 >= 0:
                url += "/"
                x = requests.post(url, data = json.dumps(data), auth = auth, headers=headers)
    
    # print("response",x.json())

    return x

def sendGETrequest(url):
    auth = getAuth(url)

    # preprocess url
    url = url +"/"
    url = url.replace("//", "/")
    url = url.replace("http", "https")
    url = url.replace("httpss", "https")
    url = url.replace("ss:", "s:")
    url = url.replace(":/", "://")

    x = requests.get(url, auth = auth)
    if x.status_code - 300 >= 0:
        url = url[:-1]
        x = requests.get(url, auth = auth)

        if x.status_code - 300 >= 0:
            url = url.replace(".com/", ".com/service/")
            x = requests.get(url, auth = auth)

            if x.status_code - 300 >= 0:
                url += "/"
                x = requests.post(url, auth = auth)

    # print(x.json())
    try:
        return x.status_code, x.json()
    except:
        return x.status_code, x

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
        elif(request.POST["context"] == "post-local"):
            return HttpResponseRedirect(reverse('local-posts-view'))
        elif(request.POST["context"] == "post-foreign"):
            return HttpResponseRedirect(reverse('foreign-posts-view'))
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
                if post["id"] == like["object"]:
                    post["numLikes"] += 1

        else:

            post["userLike"] = False
            post["numLikes"] = 0

            try:
                code, likes = sendGETrequest(post["id"] + "/likes/")

                if code - 300 < 0:
                    if("items" in likes):
                        post["numLikes"] = len(likes["items"])
                    else:
                        post["numLikes"] = len(likes)
            except MissingSchema:
                try:
                    code, likes = sendGETrequest(post["origin"] + "/likes/")

                    if code - 300 < 0:
                        if("items" in likes):
                            post["numLikes"] = len(likes["items"])
                        else:
                            post["numLikes"] = len(likes)
                except:
                    pass
    
    # Check which posts the user has already liked
    if(request.user.is_authenticated):
        likeObjects = Like.objects.filter(auth_pk = request.user)  
        userLikes = LikeSerializer(likeObjects,  many=True) 
        for post in posts:
            if "linkedspace" in post["id"]:
                for like in userLikes.data:
                    if post["id"] == like["object"]:
                        post["userLike"] = True
            else:

                try:
                
                    code, likes = sendGETrequest(post["id"] + "/likes/")

                    if code - 300 < 0:
                        if "items" in likes:
                            for like in likes["items"]:
                                if request.user.url == like["author"]["url"]:
                                    post["userLike"] = True
                        else:
                            for like in likes:
                                if request.user.url == like["author"]["url"]:
                                    post["userLike"] = True

                except MissingSchema:
                    try:
                
                        code, likes = sendGETrequest(post["origin"] + "/likes/")

                        if code - 300 < 0:
                            if "items" in likes:
                                for like in likes["items"]:
                                    if request.user.url == like["author"]["url"]:
                                        post["userLike"] = True
                            else:
                                for like in likes:
                                    if request.user.url == like["author"]["url"]:
                                        post["userLike"] = True

                    except:
                        pass
    
                

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

        if visibility == 'Friends':
            postDistributor(request, visibility, origin, uid)

        return redirect(ManagePostsList)
    else:
        # print(form.errors)
        # print(form.data)
        form = PostForm()
        context = {'form': form, 'user':request.user, 'add': True}
        return render(request, "LinkedSpace/Posts/add_post.html", context)

"""
    Helper function to distribute posts to Inboxes corresponding
    to the post preferences set by the Author of the post.
"""
def postDistributor(req, visibility, origin, uid, to_user=None):

    post = Post.objects.get(pk = uid)

    if visibility == 'Friends':
        # get authors followers list
        followers = Followers.objects.get(auth_pk=req.user).items.all() 
        for follower in followers:
            if req.user in Followers.objects.get(auth_pk=follower).items.all():
                if follower.host == origin: # send to local friends
                    inbox = Inbox.objects.get(auth_pk=follower)
                    inbox.iPosts.add(post)
                    # print(inbox.iPosts.all())
                    # print("sent to LOCAL:", follower.email)
                else: # check if author is following foreign authors
                    follow_url = follower.id + "/followers/" + req.user.auth_pk
                    data = sendGETrequest(follow_url)
                    # follow_url = "http://127.0.0.1:8000/author/7fcd83f088a941578ab31132f191de56" + "/followers/" + req.user.auth_pk
                    # print(follow_url)
                    if data["detail"]: # if author is following foreign author
                        postSerialized = PostSerializer(post)
                        inbox_url = follower.id + '/inbox'
                        # inbox_url = "http://127.0.0.1:8000/author/7fcd83f088a941578ab31132f191de56" + '/inbox'
                        # print(inbox_url)
                        sendPOSTrequest(inbox_url, postSerialized.data)
                        # print("sent to FOREIGN:", follower.email)


    if visibility == 'Private':
        to_author = Author.objects.get(pk=to_user)
        if to_author.host == origin: # send to local author inbox
            inbox = Inbox.objects.get(auth_pk=to_author)
            inbox.iPosts.add(post)
            # print(inbox.iPosts.all())
            # print("sent to LOCAL:", to_author.email)
        else: # send to foreign author inbox
            to_url = to_author.id + "/followers/" + req.user.auth_pk
            data = sendGETrequest(to_url)
            if data["detail"]:
                postSerialized = PostSerializer(post)
                inbox_url = to_author.id + '/inbox'
                sendPOSTrequest(inbox_url, postSerialized.data)
                # to_url = "http://127.0.0.1:8000/api/author/7fcd83f088a941578ab31132f191de56" + '/followers/' + req.user.auth_pk
                # to_url = "https://linkedspace-staging.herokuapp.com/api/author/4ed9968bede94f149f17a1001764f9dd/followers/f90d3e62c77d4117add66718aad5955e"
                # # follow_url = "http://127.0.0.1:8000/author/7fcd83f088a941578ab31132f191de56" + "/followers/" + req.user.auth_pk
                # # print(follow_url)
                # if sendGETrequest(to_url): # if author is following foreign author
                #     postSerialized = PostSerializer(post)
                #     # inbox_url = to_author.id + '/inbox'
                #     inbox_url = "http://127.0.0.1:8000/author/7fcd83f088a941578ab31132f191de56" + '/inbox'
                #     # print(inbox_url)
                #     sendPOSTrequest(inbox_url, postSerialized.data)
                #     # print("sent to FOREIGN:", follower.email)


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

            if contentType == "application/app" and form.cleaned_data["text"] == "": 
                content = request.FILES['file'].read() #Inputfile
            elif contentType in ["image/png", "image/jpeg",] and form.cleaned_data["text"] == "":
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

def PrivatePostView(request, auth_pk):
    form = PostForm(request.POST, request.FILES)

    if form.is_valid():
        # print("POST IS VALID IN PRIVATE POST VIEW")
        title = form.cleaned_data['title']
        descirption = form.cleaned_data['description']
        categories = form.cleaned_data['categories']
        # visibility = form.cleaned_data['visibility']
        visibility = 'Private'
        # unlisted = form.cleaned_data['unlisted']
        unlisted = False
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

        vis = 'Private'
        postDistributor(request, vis, origin, uid, auth_pk)

        return redirect(ManagePostsList)
    else:
        # print(form.errors)
        # print(form.data)
        form = PostForm()
        context = {'form': form, 'user':request.user, 'add': True}
        return render(request, "LinkedSpace/Posts/private_post.html", context)
        
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

def ForeignPostsFrontend(request):
    updateForeignAuthors()
    if request.method == 'GET':
        postsList_ = GetForeignPosts()

        fr_POSTS = []
        data = []
        postsList = []

        for i in range(len(postsList_)):
            if "items" in postsList_[i]:
                postsList.append(processLikes(request, postsList_[i]['items']))
            else:
                postsList.append(processLikes(request, postsList_[i]))

            fr_POSTS += postsList[i]

        for b in range(len(fr_POSTS)):
            d = fr_POSTS[b]
            c = d["content"]
            if "visibility" not in d:
                d["visibility"] = "Public"
            if "image" in d["contentType"]:
                d["contentType"] = "image/png"
                d["content"] =  "b'" + d["content"].split("base64,")[-1] + "'"
            if "categories" not in d or isinstance(d["categories"], str):
                d["categories"] = ["Web"]
            d["source"] = "https://linkedspace-staging.herokuapp.com/posts/connection/"
            serializerPost = PostSerializer(data=d)
            
            d["content"] = c
            if serializerPost.is_valid():
                    postSet = Post.objects.filter(id= d["id"])
                        
                    if(postSet.count() == 0):
                        serializerPost.validated_data["author"] = d["author"]
                        serializerPost.validated_data["author_id"] = Author.objects.get(id__icontains=d["author"]["id"])
                        
                        # if "comments" in d:
                        #     serializerPost.validated_data["comments"] = d["comments"]
                        
                        serializerPost.validated_data["post_pk"] = d["id"].split("/")[-1]
                        serializerPost.validated_data["id"] = d["id"]

                        serializerPost.save()

            else:
                print(serializerPost.errors)

        # team 3
        if 0 in range(-len(postsList), len(postsList)):
            for i in postsList[0]:
                # if post is image
                if 'image' in i['contentType']:
                    i["isImage"] = True
                    index = i['content'].index('base64,')
                    imgdata = i["content"][index+7:]
                    i["image"] = imgdata
                # change source and add team number and id
                i['source'] = "https://linkedspace-staging.herokuapp.com/posts/connection/"
                i['teamID'] = "3/" + i["id"].split("/")[-1]
                # get comments 
                # comment = requests.get(i['comments'], auth=('socialdistribution_t03','c404t03'))
                # try:
                #     i["allcomments"] = comment.json()['comments']
                # except:
                #     print(comment.status_code)
                
                # append into data
                data.append(i)
            
        # team 15
        if 1 in range(-len(postsList), len(postsList)):
            for i in postsList[1]:
                if 'image' in i['contentType']:
                    i["isImage"] = True
                    index = i['content'].index('base64,')
                    imgdata = i["content"][index+7:]
                    i["image"] = imgdata
                # change source and origin
                i['source'] = "https://linkedspace-staging.herokuapp.com/posts/connection/"
                i['teamID'] = "15/" + i["id"].split("/")[-1]
                # get comments 
                # url = i['comments']
                # comment = requests.get(url, auth=('connectionsuperuser','404connection'))
                #if comment.json()['comments']
                # try:
                #     i["allcomments"] = comment.json()['comments']
                # except:
                #     print(comment.status_code)
                    
                # append to data
                data.append(i)
            
        # team 17
        # need to implement comment once they have correct comment url
        if 2 in range(-len(postsList), len(postsList)):
            for i in postsList[2]:
                if 'image' in i['contentType']:
                    i["isImage"] = True
                    index = i['content'].index('base64,')
                    imgdata = i["content"][index+7:]
                    i["image"] = imgdata
                # change source and origin
                i['source'] = "https://linkedspace-staging.herokuapp.com/posts/connection/"
                i['teamID'] = "17/" + i["id"]
                # get comments
                # comment = requests.get(i['comments'], auth=('4cbe2def-feaa-4bb7-bce5-09490ebfd71a','123456'))
                # try:
                #     i["allcomments"] = comment.json()
                # except:
                #     print(comment.status_code)

                data.append(i)
        
            
        page_number = request.GET.get('page')
        if 'size' in request.GET:
            page_size = request.GET.get('size')
        else:
            page_size = 5

        for post in data:
            post["categories"] =  ' '.join(post["categories"])
            if 'social-dis' in post["id"]:
                post["author"]["url"] = post["author"]["url"].replace("https://social-dis.herokuapp.com/", "https://linkedspace-staging.herokuapp.com/")
                post["comments"] = post["comments"].replace("https://social-dis.herokuapp.com/", "https://linkedspace-staging.herokuapp.com/")
                post["id"] = post["id"].replace("https://social-dis.herokuapp.com/", "https://linkedspace-staging.herokuapp.com/")
            
            if 'unhindled' in post["id"]:
                post["author"]["url"] = post["author"]["url"].replace("https://unhindled.herokuapp.com/", "https://linkedspace-staging.herokuapp.com/")
                post["comments"] = post["comments"].replace("https://unhindled.herokuapp.com/", "https://linkedspace-staging.herokuapp.com/")
                post["id"] = post["id"].replace("https://unhindled.herokuapp.com/", "https://linkedspace-staging.herokuapp.com/")
            

                # http://127.0.0.1:8000/posts/connection/a8134b65-cc8f-4a3d-9473-3e77dc7583bf
            if 'cmput404f21t17' in post["origin"]:
                # print("HELLO TEAM 17 POSTS =================")
                # print(post["author"]["url"])
                # post["author"]["url"] = "https://linkedspace-staging.herokuapp.com/author/" + post["author"]["id"] + '/posts/' + post["id"]
                post["author"]["url"] = post["author"]["url"].replace("https://cmput404f21t17.herokuapp.com/service/", "https://linkedspace-staging.herokuapp.com/")
                post["comments"] = post["comments"].replace("https://cmput404f21t17.herokuapp.com/", "https://linkedspace-staging.herokuapp.com/")
                # post["id"] = post["id"].replace("https://cmput404f21t17.herokuapp.com/", "https://linkedspace-staging.herokuapp.com/")
                post["id"] = "https://linkedspace-staging.herokuapp.com/author/" + post["author"]["id"] + '/posts/' + post["id"]



        paginator = Paginator(data, page_size)
        page_obj = paginator.get_page(page_number)
        
        context = {'Posts':page_obj, 'local':False}

        return render(request, 'LinkedSpace/Posts/foreignposts.html', context)

def ForeignPostsComment(request, url):
    print("hi")
        
def LocalPosts(request):
    # TODO Add Github API stuff here
    
    if(request.user.is_authenticated):
        author = request.user
        localposts = Post.objects.filter(id__icontains = "linkedspace-staging") & Post.objects.filter(visibility = "Public") & Post.objects.filter(unlisted = "False")

    else:
        # TODO Friend Posts in stream
        localposts = Post.objects.filter(id__icontains = "linkedspace-staging") & Post.objects.filter(visibility = "Public") & Post.objects.filter(unlisted = "False")
    
    localposts = localposts.order_by('-published')

    posts = PostSerializer(localposts, many=True)
    
    # If Content is image
    for post in posts.data:
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata
        post["categories"] = ' '.join(post["categories"])

    posts = processLikes(request, posts.data)

    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 5

    paginator = Paginator(posts, page_size)
    page_obj = paginator.get_page(page_number)
    context = {'Posts':page_obj, 'local':True}

    return render(request, 'LinkedSpace/Posts/localPosts.html', context)
