from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

import uuid
import re

HOST = f"{settings.SERVER_URL}"

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

        if other_kwargs.get('is_staff') is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_kwargs.get('is_superuser') is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(email, displayName, password, **other_kwargs)


# Create your models here.
class Author(AbstractBaseUser, PermissionsMixin):
    # uid = uuid.uuid4().hex
    # urn = HOST + '/author/' + uid
    # auth_pk = models.UUIDField(primary_key=True, max_length=100, default=uid, editable=False)
    # id = models.CharField(max_length=200, default=urn, editable=False)
    # id = models.CharField(primary_key=True, max_length=200, default=urn, editable=False)
    # url = models.CharField(max_length=200, default=urn, editable=False)

    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=30, default='author', editable=False)
    host = models.CharField(max_length=200, default=HOST)
    displayName = models.CharField(max_length=50, editable=True)
    url = models.CharField(max_length=200, default=HOST, blank=True)
    github = models.CharField(max_length=200, default='', blank=True)

    # Required for extending AbstractUser ...
    username = None
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    # last_login = models.DateTimeField(verbose_name='last login', auto_now_add=True)
    # is_admin = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['displayName']

    objects = AuthorManager()

    def __str__(self):
        return self.email

    def get_author_url(self):
        return f'{HOST}/author/{str(self.id)}'
    
    # required functions, don't need to explicitly state these since Perm mixins will fill them in
    # def has_perm(self, perm, obj=None):
    #     return self.is_admin
    
    # def has_module_perms(self, app_label):
    #     return True

# Foreign keys: use settings.AUTH_USER_MODEL to refer to the default user model (Author)

