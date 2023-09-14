from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularYAMLAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("feeds.urls")),
    path("api/v1/", include("categories.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path("docs/json/", SpectacularJSONAPIView.as_view(), name="schema-json"),
        path("docs/yaml/", SpectacularYAMLAPIView.as_view(), name="swagger-yaml"),
        path(
            "docs/",
            SpectacularSwaggerView.as_view(url_name="schema-json"),
            name="swagger-ui",
        ),
        path(
            "docs/redoc/",
            SpectacularRedocView.as_view(url_name="schema-json"),
            name="redoc",
        ),
    ]
