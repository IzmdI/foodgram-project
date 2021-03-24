from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class UserAdminCustom(UserAdmin):
    list_filter = ("username", "email")
    search_fields = ("username", "email")


admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
