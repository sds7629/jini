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
    path("users/auth/kakao/login/", socialaccounts.kakao_login),
    path("users/auth/kakao/callback/", socialaccounts.kakao_callback),
    path("users/auth/naver/login/", socialaccounts.naver_login),
    path("users/auth/naver/callback/", socialaccounts.naver_callback),
    path("", include(router.urls)),
    # path("users/<int:pk>/signout", views.signout),
]
