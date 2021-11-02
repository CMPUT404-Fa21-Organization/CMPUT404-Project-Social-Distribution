import base64
from django.db import models
from django.db.models.deletion import CASCADE
from Author.models import Author

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

# Create your models here.
class Post(models.Model):
    post_pk = models.CharField(primary_key=True, max_length=100, editable=False)

    author_id = models.ForeignKey(Author, on_delete=CASCADE)
    author = models.JSONField(editable=False)

    id = models.CharField(max_length=200, editable=False)

    type = models.CharField(max_length=30, default='post', editable=False)
    title = models.CharField(max_length=200, editable=True)
    source = models.CharField(max_length=200, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=500, blank=True)

    content_type = (("text/markdown", "text/markdown"),
                    ("text/plain", "text/plain"),
                    ("application/app", "application/base64"),
                    ("image/png", "image/png;base64"),
                    ("image/jpeg", "image/jpeg;base64"),
                    ("HTML", "HTML"),
                    )
    contentType = models.CharField(max_length=20, choices=content_type)

    content = Base64Field()

    post_categories = (
        ('Web', 'Web'),
        ('Tutorial', 'Tutorial'),
        ('', ''),
    )
    categories = models.CharField(max_length=20, choices=post_categories, editable=False)
    count = models.PositiveBigIntegerField(default=0)
    size = models.PositiveBigIntegerField(default=10)

    comments = models.CharField(max_length=200, editable=False)

    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=20, blank=False, editable=True)
    unlisted = models.BooleanField(blank=False, default=False)
