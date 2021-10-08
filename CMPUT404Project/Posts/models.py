import base64
import uuid
import re
from django.core import serializers
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.html import escape
import json
from Author.models import Author

class Base64Field(models.TextField):
    # https://djangosnippets.org/snippets/1669/
    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.decodestring(getattr(obj, self.field_name))
    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))

# Create your models here.
class Post(models.Model):
    r_uid = uuid.uuid4().hex
    uid = re.sub('-', '', r_uid)
    post_pk = models.CharField(primary_key=True, max_length=100, default=uid, editable=False)

    author_id = models.ForeignKey(Author, on_delete=CASCADE)
    author = models.JSONField(editable=False)

    uri = 'post/' + uid

    id = models.CharField(max_length=200, editable=False)

    type = models.CharField(max_length=30, default='post', editable=False)
    title = models.CharField(max_length=200, editable=True)

    source = models.CharField(max_length=200, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=500, blank=True)

    content_type = (("markdown", "text/markdown"),
                    ("plain", "text/plain"),
                    ("app", "application/base64"),
                    ("png", "image/png;base64"),
                    ("jpeg", "image/jpeg;base64"),
                    ("html", "HTML"),
                    )
    contentType = models.CharField(max_length=20, choices=content_type, editable=False)

    #content = Base64Field()

    post_categories = (
        ('web', 'Web'),
        ('tutorial', 'Tutorial'),
        ('', ''),
    )
    categories = models.CharField(max_length=20, choices=post_categories, editable=False)
    count = models.PositiveBigIntegerField()
    size = models.PositiveBigIntegerField()

    comments_id = str(id) + '/comments'
    comments = models.JSONField(default="null")

    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=20, blank=False, editable=True)
    unlisted = models.BooleanField(blank=False, default=False)

    def image_to_b64(imagine_file):
        with open(imagine_file.path, "rb") as f:
            encoded_string = base64.b64encode(f.read())
            return encoded_string

    # def save(self, *args, **kwargs):
    #     # if self.author_id:
    #         self.author = serializers.serialize('json', Author.objects.filter(email=self.author_id))
    #         # save the contentType to the content of the file that user uploads
    #         self.contentType= "text/plain"
    #         self.content="Null"
    #         #with open("dog.jpg", "r") as f:
    #             #content = f
    #         super().save(*args, **kwargs)
'''
INSERT INTO Posts_post VALUES ("gbeuihfoewh",{"http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072","http://127.0.0.1:8000/","http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072","belton",""}
,"hjhifuhfiishf","post","test","","","","jpeg","dog.jnp", "", "234", "24","comment", "public")
'''