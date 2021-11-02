from django import forms
from django.forms import ModelForm
from .models import Post, Author
from django.core import serializers
from django.db.models.deletion import CASCADE

class PostForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(max_length=500, required=False)

    content_type = (("text/markdown", "text/markdown"),
                    ("text/plain", "text/plain"),
                    ("application/app", "application/base64"),
                    ("image/png", "image/png;base64"),
                    ("image/jpeg", "image/jpeg;base64"),
                    ("HTML", "HTML"),
                    )
    contentType = forms.CharField(max_length=20, required=True,
            widget=forms.Select(choices=content_type, attrs={'class':'dropdown-item', 'style':'width:20%; background-color:#ededed;'}))
    text = forms.CharField(required=False, widget= forms.Textarea)
    file = forms.FileField(required=False)


    categories_list = (
        ('Web', 'Web'),
        ('Tutorial', 'Tutorial'),
    )

    categories = forms.CharField(max_length=20, required=True,
        widget=forms.Select(choices=categories_list, attrs={'class':'dropdown-item', 'style':'width:20%; background-color:#ededed;'}))

    visible = (
            ('PUBLIC', 'Public'),
            ('FRIENDS', 'Friends'),
    )
    visibility = forms.CharField(max_length=20, required=True,
            widget=forms.Select(choices=visible, attrs={'class':'dropdown-item', 'style':'width:20%; background-color:#ededed;'}))
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

