from django.contrib import admin
from .models import Node

# Register your models here.
class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'remote_server_url')
    ordering = ('team',)

admin.site.register(Node, NodeAdmin)