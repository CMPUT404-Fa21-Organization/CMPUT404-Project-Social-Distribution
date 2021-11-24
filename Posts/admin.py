from django.contrib import admin
from .models import Post

from .models import Post
# Register your models here.
class PostAdmin(admin.ModelAdmin):
    class Meta: 
        model = Post
        fields = "__all__"

    list_display = ('author_id', 'title', 'contentType', 'categories', 'published')

admin.site.register(Post, PostAdmin)
