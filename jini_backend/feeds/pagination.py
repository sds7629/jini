from django.core.paginator import InvalidPage
from rest_framework.pagination import (
    BasePagination,
    PageNumberPagination,
    CursorPagination,
)
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from collections import OrderedDict


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"

    def paginate_queryset(self, queryset, request, view=None):
        # page_size = self.get_page_size(request)
        # if not page_size:
        #     return None
        page_size = 5

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as e:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(e)
            )
            raise NotFound(msg)

        return list(self.page)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict([("count", self.page.paginator.count), ("results", data)])
        )


# class CursorPagination(CursorPagination):
#     page_size = 5
#     cursor_query_param = "page"
#     page_size_query_param = "page_size"
#     ordering = "created_at"
