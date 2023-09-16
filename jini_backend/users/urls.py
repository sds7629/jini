from django.urls import path, include
from rest_framework import routers
from . import views
from . import socialaccounts

app_name = "users"

router = routers.SimpleRouter()
router.register(r"users", views.UserViewSet)

urlpatterns = [
    path("users/my_info/", views.get_info),
    path("users/auth/google/login/", socialaccounts.google_login),
    path("users/auth/google/callback/", socialaccounts.google_callback),
    path("", include(router.urls)),
    # path("users/<int:pk>/signout", views.signout),
]
