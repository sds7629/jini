from django.contrib import admin
from .models import Feed


@admin.register(Feed)
class UserAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
