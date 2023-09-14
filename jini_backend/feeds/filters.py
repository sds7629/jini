from django_filters import FilterSet, CharFilter, OrderingFilter
from .models import Feed


class FeedFilter(FilterSet):
    writer__nickname = CharFilter(
        field_name="writer", lookup_expr="nickname__icontains"
    )

    class Meta:
        model = Feed
        fields = ("writer",)
