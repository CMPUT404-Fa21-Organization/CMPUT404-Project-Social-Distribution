from django.db import models
import uuid

# Create your models here.
class Node(models.Model):

    id = models.CharField(primary_key=True, max_length=200, default=uuid.uuid4, editable=True)
    password = models.CharField(max_length=200, blank=False)
    connected_server_url = models.URLField(max_length=200, default='', blank=True)

    CHOICES = [(i,i) for i in range(1,27)]

    team = models.IntegerField(choices=CHOICES, blank=True)

