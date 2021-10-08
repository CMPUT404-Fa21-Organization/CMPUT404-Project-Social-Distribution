from django import forms
from .models import Post, Author, Base64Field
from django.core import serializers

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