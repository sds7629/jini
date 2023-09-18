from django_filters import FilterSet, CharFilter, BooleanFilter
from .models import Feed


class FeedFilter(FilterSet):
    nickname = CharFilter(
        field_name="writer",
        lookup_expr="nickname__icontains",
    )
    category = CharFilter(
        field_name="category",
        lookup_expr="kind__icontains",
    )

    class Meta:
        model = Feed

        fields = (
            "writer",
            "category",
        )
