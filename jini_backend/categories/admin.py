from django.contrib import admin
from .models import Category


@admin.register(Category)
class UserAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
