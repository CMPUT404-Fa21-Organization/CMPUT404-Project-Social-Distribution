from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Author, Inbox

# Register your models here.
class AuthorAdmin(UserAdmin):
    # display fields
    fieldsets = (
        (None, {'fields': ('email', 'displayName','password')}),
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
    list_display = ('email', 'auth_pk', 'displayName', 'is_staff', 'url')


# admin.site.unregister(User)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Inbox)