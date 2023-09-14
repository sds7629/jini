from collections.abc import Collection
from rest_framework.exceptions import ParseError
from django.db import models
from django.conf import settings
from common.models import Common


class Feed(Common):
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="feeds",
    )
    title = models.CharField(max_length=35)
    content = models.TextField()
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="feeds",
    )
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="feed_like",
        null=True,
        blank=True,
    )
    file = models.URLField(null=True, blank=True)
    is_secret = models.BooleanField(default=True)

    def __str__(self):
        return self.title
