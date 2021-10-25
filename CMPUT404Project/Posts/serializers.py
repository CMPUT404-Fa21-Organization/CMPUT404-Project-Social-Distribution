from django.db.models import fields
from rest_framework import serializers
from .models import Post
from commentModel import *

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'type',
            'title',
            'id',
            'source',
            'origin',
            'description',
            'contentType',
            'content',
            'author',
            'categories',
            'count',
            'size',
            'comments',
            'published',
            'visibility',
            'unlisted',
        )

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = (
            'type',
            'id',
            'contentType',
            'content',
            'author'
            'size'
            'unlisted'
        )
