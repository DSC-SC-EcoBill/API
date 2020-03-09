from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Users


class UsersInline(admin.StackedInline):
    model = Users
    can_delete = False
    verbose_name_plural = 'Users'


class UserAdmin(BaseUserAdmin):
    inlines = (UsersInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
