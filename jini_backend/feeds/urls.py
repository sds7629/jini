from django.urls import path, include

# from rest_framework import routers
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register("feeds", views.FeedViewSet)
# router.register("review", views.ReviewViewSet)
review_router = routers.NestedSimpleRouter(
    router,
    r"feeds",
    lookup="feed",
)
review_router.register(
    r"reviews",
    views.ReviewViewSet,
    basename="feed-review",
)

app_name = "feeds"


urlpatterns = [
    path("feeds/<int:feed_pk>/likes/", views.likes),
    path("updel_reply/<int:reply_pk>/", views.updel_reply),
    path("feeds/mysecret/", views.my_secret_feed),
    path("feeds/mysecret/<int:pk>/", views.my_secret_del),
    path("", include(router.urls)),
    path("", include(review_router.urls)),
]
