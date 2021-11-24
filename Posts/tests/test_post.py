from django.test import TestCase
from Posts.models import Post
from Author.models import Author
from django.utils import timezone
from django.core import serializers
import json
import uuid
import re


from rest_framework import status 
from rest_framework.test import APIClient
from django.db import IntegrityError
# Create your tests here.

""" Command line examples for executing tests
Run specified module: python3 manage.py test Posts.tests
"""

class PostTest(TestCase):

    ## include the right author auth
    def test_create_post(self):
        Post.objects.all().delete()
        Author.objects.all().delete()
        author = Author.objects.create_user(email='testauthor@email.com', displayName="Test Author", password="testpassword")
        published = timezone.now()
        authorJson = json.loads(serializers.serialize('json', Author.objects.filter(id=author.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']

        r_uid = uuid.uuid4().hex
        uid = re.sub('-', '', r_uid)
        postid = authorJson.get("id") + '/posts/' + uid

        post = Post.objects.create(id=postid, author_id=author, author=authorJson, title="post with auth", source="no source", origin="still idk", description="not available", contentType="plain", count=0, size=10, visibility="Public", unlisted="False", published=published, content="this should be valid content")
        poststuff = json.loads(serializers.serialize('json', Post.objects.filter(id=post.id), fields=( 'type','title','id','source','origin','description','contentType','content','author','categories','count','size','comments','published','visibility', 'unlisted',)))[0]['fields']
        self.assertEqual(Post.objects.filter(pk=post.pk)) 

    def test_post_image(self):
        Post.objects.all().delete()
        Author.objects.all().delete()
        author = Author.objects.create_user(email='testauthor@email.com', displayName="Test Author", password="testpassword")
        published = timezone.now()
        authorJson = json.loads(serializers.serialize('json', Author.objects.filter(id=author.id), fields=('type', 'id', 'host', 'url', 'github',)))[0]['fields']

        r_uid = uuid.uuid4().hex
        uid = re.sub('-', '', r_uid)
        postid = authorJson.get("id") + '/posts/' + uid
        with open("./dog.jpg", "rb") as f:
            content = f.read()
        post = Post.objects.create(id=postid, author_id=author, author=authorJson, title="post an image", source="no source", origin="still idk", description="not available", contentType="jpg", count=0, size=10, visibility="Public", unlisted="False", published=published, content=content)
        poststuff = json.loads(serializers.serialize('json', Post.objects.filter(id=post.id), fields=( 'type','title','id','source','origin','description','contentType','content','author','categories','count','size','comments','published','visibility', 'unlisted',)))[0]['fields']
        #print(poststuff)
        self.assertTrue(Post.objects.filter(pk=post.pk))

class AuthorAPITest(TestCase):
    client = APIClient()
    Author.objects.all().delete()
    Post.objects.all().delete()
    author = Author.objects.create_user(email='testauthor@email.com', displayName="Test Author", password="testpassword")
    authorJson = json.loads(serializers.serialize('json', Author.objects.filter(id=author.id), fields=('type', 'id', 'host', 'url', 'github',)))

    r_uid = uuid.uuid4().hex
    uid = re.sub('-', '', r_uid)
    postid = authorJson[0]['fields'].get("id") + '/posts/' + uid
    published = timezone.now()

    test_author = {
        'email':'testauthor@email.com',
        'displayName':'Test Author',
        'password':'testpassw0rd',
    }
    test_post = {
        'type':'post',
        'title':'test title',
        #'id': postid,
        'source':'idk',
        'origin':'not sure',
        'description':'testing',
        'contentType':'plain',
        'content':'testing content',
        'count':0,
        'size':10,
        'visibility':'Public',
        'unlisted':'False',
    }

    #def test_post_endpoint(self):
        #print(self.postid)
        #request = self.client.post(f'/author/{self.author.auth_pk}/posts/add_post/', self.test_post)
        #print(request)
        #self.assertFalse(request.status_code == 200)
       