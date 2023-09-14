from django_filters.filters import OrderingFilter
from django_filters import FilterSet, CharFilter
from django.contrib.auth import get_user_model


class NicknameFilter(FilterSet):
    nickname = CharFilter(field_name="nickname", lookup_expr="nickname")

    class Meta:
        model = get_user_model()
        fields = ("nickname",)