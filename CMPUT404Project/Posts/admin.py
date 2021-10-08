from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from .models import Post
import base64
from .form import PostCreationForm

class postAdmin(admin.ModelAdmin):
    list_display = (
        'post_pk',
        'author_id',
        'author',
        'type',
        'title',
        'source',
        'origin',
        'description',
        'contentType',
        #'content',
        'categories',
        'count',
        'size',
        'comments',
        'published',
        'visibility',
        'unlisted',
    )
    exclude = ["content"]
    #readonly_fields = ["content",]
    #form = PostCreationForm

    # def content(self, obj):
    #     base64Encoded = base64.b64encode(obj.logo)
    #     return format_html('<img src="data:;base64,{}">', base64Encoded)



# Register your models here.
admin.site.register(Post)
