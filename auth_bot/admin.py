from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "telegram_id")


class AuthCodeAdmin(admin.ModelAdmin):
    list_display = ("user",)


admin.site.register(User, UserAdmin)
admin.site.register(AuthCode, AuthCodeAdmin)
