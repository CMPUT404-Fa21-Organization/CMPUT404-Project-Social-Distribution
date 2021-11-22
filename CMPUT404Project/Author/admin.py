from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
def set_active(modeladmin, request, queryset):
    for user in queryset:
        user.is_active = True
        user.save()

set_active.short_description = 'Set Status: Activated'

def deactivate(modeladmin, request, queryset):
    for user in queryset:
        user.is_active = False
        user.save()

deactivate.short_description = 'Set Status: Deactivated'

class AuthorAdmin(UserAdmin):
    # display fields
    fieldsets = (
        (None, {'fields': ('email', 'displayName','github')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)
    search_fields = ('email', 'displayName')
    # list_display = ('email', 'displayName', 'is_staff', 'url')
    list_display = ('email', 'auth_pk', 'displayName', 'github', 'is_active', 'is_staff', 'url')
    actions = [set_active, deactivate,]


# admin.site.unregister(User)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Inbox)
admin.site.register(Like)
admin.site.register(Liked)
admin.site.register(FriendRequest)
admin.site.register(Followers)