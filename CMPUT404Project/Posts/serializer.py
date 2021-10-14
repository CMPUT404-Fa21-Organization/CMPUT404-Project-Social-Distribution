from rest_framework import serializers
from rest_framework.views import exception_handler
from django.contrib.auth import authenticate
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "postData",
        )
