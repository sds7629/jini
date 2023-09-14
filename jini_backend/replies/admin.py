from django.contrib import admin
from .models import Reply


@admin.register(Reply)
class UserAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
