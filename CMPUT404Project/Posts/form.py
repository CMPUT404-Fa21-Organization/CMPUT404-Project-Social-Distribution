from django import forms
from django.forms import ModelForm
from .models import Comments, Post, Author
from django.core import serializers
from django.db.models.deletion import CASCADE

class PostForm(forms.Form):
    title = forms.CharField(max_length=200)
    source = forms.CharField(max_length=200, required=False)
    origin = forms.CharField(max_length=200, required=False)
    description = forms.CharField(max_length=500, required=False)

    text = forms.CharField(required=False)
    file = forms.FileField(required=False)

    visibility = forms.CharField(max_length=20, required=True)
    unlisted = forms.BooleanField(required=False)

    fields = [
            'title',
            'source',
            'origin',
            'description',
            'file',
            'count',
            'size',
            'visibility',
            'unlisted',]

class PostFormTest(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'source', 'origin', 'description', 'count', 'size', 'visibility', 'unlisted',]
        # exclude = ('author_id','author', 'type', 'contentType', 'content', 'catergories', 'comments_id', 'comments', 'pulished',)

'''
# comment form
class CommentForm(forms.ModelForm):
    text = forms.CharField(required=False)
    file = forms.FileField(required=False)
    unlisted = forms.BooleanField(required=False)
    
    fields = [
        #'page'
        #'size',
        'file',
        'unlisted'
    ]
'''

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

