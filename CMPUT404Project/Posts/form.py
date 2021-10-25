from django import forms
from django.forms import ModelForm
from .models import Post, Author
from django.core import serializers
from django.db.models.deletion import CASCADE

class PostForm(forms.Form):
    title = forms.CharField(max_length=200)
    source = forms.CharField(max_length=200, required=False)
    origin = forms.CharField(max_length=200, required=False)
    description = forms.CharField(max_length=500, required=False)

    content_type = (("markdown", "text/markdown"),
                    ("plain", "text/plain"),
                    ("app", "application/base64"),
                    ("png", "image/png;base64"),
                    ("jpeg", "image/jpeg;base64"),
                    ("html", "HTML"),
                    )
    contentType = forms.CharField(max_length=20, required=True,
            widget=forms.Select(choices=content_type))
    text = forms.CharField(required=False)
    file = forms.FileField(required=False)


    visible = (
            ('PUBLIC', 'Public'),
            ('FRIENDS', 'Friends'),
    )
    visibility = forms.CharField(max_length=20, required=True,
            widget=forms.Select(choices=visible))
    unlisted = forms.BooleanField(required=False)

    fields = [
            'title',
            'source',
            'origin',
            'description',
            'count',
            'size',
            'visibility',
            'unlisted',]

class contentForm(ModelForm):
    pass

class PostFormTest(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'source', 'origin', 'description', 'count', 'size', 'visibility', 'unlisted',]
        # exclude = ('author_id','author', 'type', 'contentType', 'content', 'catergories', 'comments_id', 'comments', 'pulished',)

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
            'count',
            'size',
            # 'comments',
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
