from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "users"

router = routers.SimpleRouter()
router.register(r"users", views.UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # path("users/<int:pk>/signout", views.signout),
]
