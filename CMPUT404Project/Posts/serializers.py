from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
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
