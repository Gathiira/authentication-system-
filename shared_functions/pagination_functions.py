from rest_framework.pagination import PageNumberPagination
from django.db.models import QuerySet
from functools import wraps
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20


def paginate_results(func):

    @wraps(func)
    def inner(self, *args, **kwargs):
        queryset = func(self, *args, **kwargs)
        try:
            assert isinstance(queryset, (list, QuerySet)
                              ), "apply_pagination expects a List or a QuerySet"
        except Exception:
            queryset = []

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    return inner
