from django.db import models

# Create your models here.

class Post(models.Model):
  postData = models.CharField(max_length=200)
