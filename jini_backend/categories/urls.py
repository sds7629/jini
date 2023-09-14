from django.urls import path, include
from . import views

urlpatterns = [
    path("category/", views.CategoryView),
    path("category/<str:name>/", views.DetailCategoryView),
]
