from rest_framework import serializers
from .models import Author, Inbox

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = (
            'type',
            'id',
            'host',
            'url',
            'displayName',
            'github',
        )

class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = (
            'author',
            'type',
            'items',
        )