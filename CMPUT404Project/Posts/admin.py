from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from .models import Post, Author
import base64

class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'author_id',
            'title',
            'source',
            'origin',
            'description',
            # 'content',
            'count',
            'size',
            'comments',
            'visibility',
            'unlisted',]
        author = forms.JSONField()

        def set_author(self, author):
            data = self.data.copy()
            data['author'] = author
            self.data = data

class postAdmin(admin.ModelAdmin):
    list_display = (
        'post_pk',
        'author_id',
        'author',
        'type',
        'title',
        'source',
        'origin',
        'description',
        'contentType',
        # 'content',
        'categories',
        'count',
        'size',
        'comments',
        'published',
        'visibility',
        'unlisted',
    )

# Register your models here.
admin.site.register(Post)
