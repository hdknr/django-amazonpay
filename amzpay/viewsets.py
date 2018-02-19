from rest_framework import (viewsets, response, permissions, pagination)
from social_django.utils import load_strategy, load_backend
from social_django.views import _do_login
from collections import OrderedDict
from . import models, serializers, filters


class Pagination(pagination.PageNumberPagination):
    page_size = 16
    max_page_size = 16
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return response.Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('page_range', list(self.page.paginator.page_range)),
            ('current_page', self.page.number),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class TokenViewSet(viewsets.ViewSet):

    def auth(self, request):
        backend = load_backend(load_strategy(request), 'amazon', '')
        user = request.user if request.user.is_authenticated else None
        res = backend.do_auth(
            request.data.get('access_token', ''),
            response=request.data, user=user, request=request)
        _do_login(backend, res, getattr(res, 'social_user', None))
        return res

    def create(self, request):
        user = self.auth(request)
        return response.Response(dict(username=user and user.username))


class PayOrderViewSet(viewsets.ModelViewSet):
    queryset = models.PayOrder.objects.order_by('-updated_at')
    serializer_class = serializers.PayOrderSerializer
    filter_class = filters.PayOrderFilter
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
