from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, EmailField
from django.shortcuts import get_object_or_404

import uuid
import re

HOST = f"{settings.SERVER_URL}/"

# https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#substituting-a-custom-user-model

class AuthorManager(BaseUserManager):
    def create_user(self, email, displayName, password, **other_kwargs):
        # validate 
        if not email:
            raise ValueError("Authors must enter a valid email address.")
        # if not displayName:
        #     raise ValueError("Authors must have a display name.")

        email = self.normalize_email(email)
        user = self.model(email=email, displayName=displayName, **other_kwargs)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, displayName, password, **other_kwargs):

        other_kwargs.setdefault('is_staff', True)
        other_kwargs.setdefault('is_superuser', True)
        other_kwargs.setdefault('is_admin_approved', True)

        if other_kwargs.get('is_staff') is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_kwargs.get('is_superuser') is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")
        if other_kwargs.get('is_admin_approved') is not True:
            raise ValueError("Superuser must be assigned to is_admin_approved=True.")

        return self.create_user(email, displayName, password, **other_kwargs)


# Create your models here.
class Author(AbstractBaseUser, PermissionsMixin):
    # generate uuid string ...
    r_uid = uuid.uuid4().hex
    uid = re.sub('-', '', r_uid)
    uri = HOST + 'author/' + uid

    auth_pk = models.CharField(primary_key=True, max_length=100, default=uid, editable=False)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    id = models.CharField(max_length=200, default=uri, blank=False, editable=False, unique=True)
    type = models.CharField(max_length=30, default='author', editable=False)
    host = models.CharField(max_length=200, default=HOST)
    displayName = models.CharField(max_length=50, editable=True)
    url = models.CharField(max_length=200, default=uri, blank=False, editable=False)
    github = models.CharField(max_length=200, default='', blank=True)
    is_admin_approved = models.BooleanField(default=False)

    # Required for extending AbstractUser ...
    username = None
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['displayName']

    objects = AuthorManager()

    def __str__(self):
        return self.email

    def get_author_url(self):
        return f'{HOST}author/{str(self.auth_pk)}'

class Inbox(models.Model):
    r_uid = uuid.uuid4().hex
    uid = re.sub('-', '', r_uid)
    auth_pk= models.ForeignKey(Author, default=uid, on_delete=CASCADE, primary_key=True)
    type = models.CharField(max_length=30, default='inbox', editable=False)
    items = models.ManyToManyField("Posts.Post", default=list, blank=True)

    def get_author(self):
        return Author.objects.get(email=self.auth_pk).get_author_url()


