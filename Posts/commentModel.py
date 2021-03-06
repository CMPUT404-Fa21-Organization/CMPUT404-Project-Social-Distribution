import base64
import uuid
import re
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils import tree
from Author.models import Author
from Posts.models import Post

class Base64Field(models.TextField):
    # https://djangosnippets.org/snippets/1669/
    _data = models.TextField(
            db_column='data',
            blank=True)

    def set_data(self, data):
        self._data = base64.b64encode(data)

    def get_data(self):
        return self._data.decode('utf-8')

    data = property(get_data, set_data)

class Comments(models.Model):
    comment_pk = models.CharField(primary_key=True, max_length=100, editable=False)

    Post_pk = models.ForeignKey(Post, on_delete=CASCADE, blank=True, null=True, related_name ='comment')
    Post_pk_str = models.CharField(max_length=300, editable=False)
    auth_pk_str = models.CharField(max_length=300, blank=True, null=True ,editable=False)
    author = models.JSONField(editable=False)

    id = models.CharField(max_length=200, editable=False)

    type = models.CharField(max_length=30, default='comment', editable=False)
    size = models.PositiveBigIntegerField(default=10)

    content_type = (("text/markdown", "text/markdown"),
                    ("text/plain", "text/plain"),
                    ("application/app", "application/base64"),
                    ("image/png", "image/png;base64"),
                    ("image/jpeg", "image/jpeg;base64"),
                    ("HTML", "HTML"),
                    )

    contentType = models.CharField(max_length=20, choices=content_type, editable=False)
    content = Base64Field()
    published = models.DateTimeField(auto_now_add=True)

