from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """Standard paginator class for rest_framework API with the following pagination parameters:
        * page_size: 50
        * max_page_size: 1000
        * page_size_query_param: page_size
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total_count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('count', len(data)),
            ('results', data),
        ]))
