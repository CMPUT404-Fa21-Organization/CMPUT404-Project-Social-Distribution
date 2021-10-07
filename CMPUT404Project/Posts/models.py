import base64
import uuid
import re
from django.core import serializers
from django.db import models
from django.db.models.deletion import CASCADE
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

    content_type = (("", "text/markdown"),
                    ("", "text/plain"),
                    ("", "application/base64"),
                    ("", "image/png;base64"),
                    ("", "image/jpeg;base64"),
                    ("", "HTML"),
                    )
    contentType = models.CharField(max_length=20, choices=content_type, editable=False)

    # content = Base64Field()

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

    def save(self, *args, **kwargs):
        if self.author_id:
            self.author = serializers.serialize('json', Author.objects.filter(email=self.author_id))
            super().save(*args, **kwargs)
