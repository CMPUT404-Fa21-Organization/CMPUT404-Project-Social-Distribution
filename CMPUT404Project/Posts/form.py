from django import forms
from .models import Post, Author, Base64Field
from django.core import serializers
import uuid
import re
from django.db.models.deletion import CASCADE

# for the future post form
class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'author_id',
            'title',
            'source',
            'origin',
            'description',
            #'content',
            'count',
            'size',
            'comments',
            'visibility',
            'unlisted',]
        author = forms.JSONField()
        
        def set_author(self, author):
            data = self.data.copy()
            data['author'] = serializers.serialize('json', Author.objects.filter(auth_id =data["email"]).values())
            self.data = data

        def set_content(self, content):
            data = self.data.copy()
            with open("dog.jpg", "r") as f:
                content = f
            data['content'] = content.data_base64
            self.data = data

class PostFormTest(forms.Form):
    r_uid = uuid.uuid4().hex
    uid = re.sub('-', '', r_uid)
    uri = 'post/' + uid
    content_type = (("markdown", "text/markdown"),
                    ("plain", "text/plain"),
                    ("app", "application/base64"),
                    ("png", "image/png;base64"),
                    ("jpeg", "image/jpeg;base64"),
                    ("html", "HTML"),
                    )
    post_categories = (
        ('web', 'Web'),
        ('tutorial', 'Tutorial'),
        ('', ''),
    )

    title = forms.CharField(max_length=200)
    source = forms.CharField(max_length=200, required=False)
    origin = forms.CharField(max_length=200, required=False)
    description = forms.CharField(max_length=500, required=False)
    count = forms.IntegerField(min_value=0)
    size = forms.IntegerField(min_value=0)

    visibility = forms.CharField(max_length=20, required=True)
    unlisted = forms.BooleanField(required=True)

    fields = [
            'title',
            'source',
            'origin',
            'description',
            #'content',
            'count',
            'size',
            'visibility',
            'unlisted',]


from django.forms import ModelForm

class PostForm(ModelForm):
    class Meta:
        model = Post
        exclude = ('author_id','author', 'type', 'contentType', 'catergories', 'comments_id', 'comments', 'pulished',)