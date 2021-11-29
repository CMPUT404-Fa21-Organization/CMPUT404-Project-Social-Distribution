from django.conf import settings
from django.core import serializers
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect, render

from Posts.commentModel import Comments
from .serializers import PostSerializer
from Author.serializers import LikeSerializer
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

# Create your views here.

def PostDetailView(request, post_pk, auth_pk = None):

    user = None
    if(request.user.is_authenticated):
        user = request.user

    postObj = Post.objects.get(pk = post_pk)
    postSeririaliezed = PostSerializer(postObj, many=False)
    post = postSeririaliezed.data


    # TODO Add logic to check for friend
    if(postObj.visibility == "Public" or user == postObj.author_id):
    
        # If Content is image
        
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata

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


        context = {'post':post, 'user':user}

        template_name = 'LinkedSpace/Posts/post_detail.html'
        return HttpResponse(render(request, template_name, context),status=200)
    
    else:
        return HttpResponse(status=401)

    

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
        postsObjects = Post.objects.filter(author_id=author.pk, visibility = "Public")
    
    postsObjects = postsObjects.order_by('-published')

    posts = PostSerializer(postsObjects, many=True)
    
    # If Content is image
    for post in posts.data:
        post["isImage"] = False
        if(post["contentType"] == "image/png" or post["contentType"] == "image/jpeg"):
            post["isImage"] = True
            imgdata = post["content"][2:-1]
            post["image"] = imgdata

    # Like Stuff
    # Calculte Number of Likes for Posts
    likeObjects = Like.objects.all()  
    likes = LikeSerializer(likeObjects,  many=True)   
    for post in posts.data:
        post["userLike"] = False
        post["numLikes"] = 0
        for like in likes.data:
            if post["id"] == like["object"]:
                post["numLikes"] += 1
    
    # Check which posts the user has already liked
    if(request.user.is_authenticated):
        likeObjects = Like.objects.filter(auth_pk = request.user)  
        userLikes = LikeSerializer(likeObjects,  many=True) 
        for post in posts.data:
            for like in userLikes.data:
                if post["id"] == like["object"]:
                    post["userLike"] = True

    page_number = request.GET.get('page')
    if 'size' in request.GET:
        page_size = request.GET.get('size')
    else:
        page_size = 5

    paginator = Paginator(posts.data, page_size)
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

        posts = Post(pk=uid, id=id, author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, contentType=contentType, count=0, size=10, categories=categories,visibility=visibility, unlisted=unlisted, published=published, content=content, comments=comments_id)
        posts.save()

        return redirect(ManagePostsList)
    else:
        print(form.errors)
        print(form.data)
        form = PostForm()
        context = {'form': form, 'user':request.user, 'add': True}
        return render(request, "LinkedSpace/Posts/add_post.html", context)

def ManagePostsList(request, auth_pk=None):
    posts = Post.objects.filter(author_id=request.user).order_by('-published')
    # posts = Post.objects.all().order_by('-published')

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
            post.categories = categories
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
            context = {'form': form, 'user':request.user, 'add': True}
            return render(request, "LinkedSpace/Posts/add_post.html", context)
    else:
        form = PostForm()
        post = Post.objects.get(post_pk=post_pk)
        if request.user.id == post.author['id']:
            context = {'form': form, 'user':request.user, 'add': False, 'post': post}
            return render(request, "LinkedSpace/Posts/add_post.html", context)
        else:
            return redirect(ManagePostsList)
