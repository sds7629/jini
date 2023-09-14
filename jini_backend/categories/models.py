from django.db import models
from common.models import Common


class Category(Common):
    class CategoryChoice(models.TextChoices):
        장소 = ("place", "장소")
        글귀 = ("phrase", "글귀")
        여행지 = ("travel", "여행")
        노래 = ("sing", "노래")
        영화_드라마 = ("movie_drama", "영화_드라마")
        게임 = ("game", "게임")
        추억 = ("memory", "추억")
        그림 = ("paint", "그림")
        아이디어 = ("idea", "아이디어")
        음식 = ("food", "음식")
        취미 = ("hobby", "취미")

    name = models.CharField(max_length=15)
    kind = models.CharField(
        max_length=15,
        choices=CategoryChoice.choices,
    )

    def __str__(self):
        return f"{self.kind}"
