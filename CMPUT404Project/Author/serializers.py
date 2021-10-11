from rest_framework import serializers
from rest_framework.views import exception_handler
from django.contrib.auth import authenticate
from .models import Author, Inbox
from Posts.serializer import PostSerializer

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

# https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling
# class AuthorUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Author
#         fieldsfields = ('__all__')

#     def update(self, instance, validated_data):
#         author = instance.id
#         auth_author = self.context['request'].user.id

#         if author != auth_author:
#             raise serializers.ValidationError({'Error': 'Permission denied.'})

#         mod_author = super().update(instance, validated_data)

#         return mod_author

class AuthorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('email', 'displayName', 'date_joined') # maybe we could add follower/friend count to this???
        extra_kwargs = { # displayName is the only writeable field
            'email': {'read_only': True},
            'date_joined': {'read_only': True}
        }

class AuthorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('email', 'displayName', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        author = Author.objects.create_user(
            validated_data['email'], 
            validated_data['displayName'], 
            validated_data['password']
        )

        return author

class AuthorLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = Author
        fields = ('email', 'password')

    def validate(self, attributes):
        email = attributes.get('email')
        password = attributes.get('password')

        author = authenticate(
            request=self.context.get('request'),
            email=email, 
            password=password,
        )
        if not author:
            raise serializers.ValidationError({"Error": "Incorrect credentials provided."})
        
        attributes['user'] = author
        
        return attributes

class InboxSerializer(serializers.ModelSerializer):
    items = PostSerializer(read_only=True, many=True)
    class Meta:
        model = Inbox
        fields = (
            'author',
            'type',
            'items',
        )

