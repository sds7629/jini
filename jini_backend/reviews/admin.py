from django.contrib import admin
from .models import Review


@admin.register(Review)
class UserAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
