from django.db import models
from django.conf import settings
from common.models import Common


class Reply(Common):
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    content = models.TextField()
    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="replies",
    )
